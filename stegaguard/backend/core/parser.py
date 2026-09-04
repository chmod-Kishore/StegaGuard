"""Model file parser — loads .safetensors, .pt, and .onnx weight files."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

import numpy as np

from models.scan import ModelMetadata


def _sha256(path: str | Path) -> str:
    """Compute the SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _filter_weights(weights: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Keep only tensors with ndim >= 1 and more than 10 elements."""
    return {
        name: arr
        for name, arr in weights.items()
        if arr.ndim >= 1 and arr.size > 10
    }


# ── format-specific loaders ──────────────────────────────────────────


def _load_safetensors(path: str | Path) -> dict[str, np.ndarray]:
    try:
        from safetensors.numpy import load_file
    except ImportError as exc:
        raise ImportError(
            "safetensors is required to load .safetensors files. "
            "Install it with: pip install safetensors"
        ) from exc

    return dict(load_file(str(path)))


def _load_pytorch(path: str | Path) -> dict[str, np.ndarray]:
    try:
        import torch
    except ImportError as exc:
        raise ImportError(
            "PyTorch is required to load .pt files. "
            "Install it with: pip install torch"
        ) from exc

    data: Any = torch.load(str(path), map_location="cpu", weights_only=True)

    # Handle bare state_dict or a checkpoint dict with a 'state_dict' key.
    if isinstance(data, dict) and "state_dict" in data:
        data = data["state_dict"]

    if not isinstance(data, dict):
        raise ValueError(
            "PyTorch file does not contain a state_dict at the top level."
        )

    weights: dict[str, np.ndarray] = {}
    for name, tensor in data.items():
        try:
            weights[name] = tensor.detach().cpu().numpy()
        except Exception:
            # Skip non-numeric / non-convertible entries.
            continue
    return weights


def _load_onnx(path: str | Path) -> dict[str, np.ndarray]:
    try:
        import onnx
        from onnx import numpy_helper
    except ImportError as exc:
        raise ImportError(
            "onnx is required to load .onnx files. "
            "Install it with: pip install onnx"
        ) from exc

    model = onnx.load(str(path))
    weights: dict[str, np.ndarray] = {}
    for initializer in model.graph.initializer:
        weights[initializer.name] = numpy_helper.to_array(initializer)
    return weights


# ── public API ────────────────────────────────────────────────────────


_EXT_TO_FORMAT = {
    ".safetensors": "safetensors",
    ".pt": "pytorch",
    ".pth": "pytorch",
    ".bin": "pytorch",
    ".onnx": "onnx",
}

_LOADERS = {
    "safetensors": _load_safetensors,
    "pytorch": _load_pytorch,
    "onnx": _load_onnx,
}


def parse_model(path: str | Path) -> tuple[dict[str, np.ndarray], ModelMetadata]:
    """Parse a model weight file and return (filtered_weights, metadata).

    Supported formats: .safetensors, .pt / .pth / .bin (PyTorch), .onnx.

    Raises
    ------
    FileNotFoundError
        If *path* does not point to an existing file.
    ValueError
        If the file extension is not recognized.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Model file not found: {path}")

    ext = path.suffix.lower()
    fmt = _EXT_TO_FORMAT.get(ext)
    if fmt is None:
        raise ValueError(
            f"Unsupported model format '{ext}'. "
            f"Supported extensions: {', '.join(sorted(_EXT_TO_FORMAT))}"
        )

    loader = _LOADERS[fmt]
    raw_weights = loader(path)
    weights = _filter_weights(raw_weights)

    total_params = sum(arr.size for arr in weights.values())
    file_hash = _sha256(path)
    file_size = os.path.getsize(path)

    metadata = ModelMetadata(
        filename=path.name,
        format=fmt,
        file_size_bytes=file_size,
        total_params=total_params,
        layer_count=len(weights),
        file_hash=file_hash,
    )

    return weights, metadata
