"""Shannon entropy analysis per model layer.

Computes full-byte and LSB-only entropy to detect steganographic
payloads hidden in neural network weight tensors.
"""

import logging
import math
from typing import Dict

import numpy as np

logger = logging.getLogger(__name__)

MIN_ELEMENTS = 100
LSB_ENTROPY_THRESHOLD = 6.5
SIGMA_THRESHOLD = 2.0


def _shannon_entropy(byte_array: np.ndarray) -> float:
    """Compute Shannon entropy (bits) over a uint8 array."""
    if len(byte_array) == 0:
        return 0.0
    _, counts = np.unique(byte_array, return_counts=True)
    probs = counts / counts.sum()
    # Filter out zero probabilities to avoid log2(0)
    probs = probs[probs > 0]
    entropy = -float(np.sum(probs * np.log2(probs)))
    return abs(entropy)  # normalize -0.0 to 0.0


def _extract_lsb_bytes(byte_array: np.ndarray) -> np.ndarray:
    """Extract the least significant byte of each float32.

    In little-endian representation, the LSB of each 4-byte float32 is
    at index 0, 4, 8, ... (every 4th byte starting at offset 0).
    """
    if len(byte_array) < 4:
        return byte_array
    return byte_array[0::4]


def analyze(weights: Dict[str, np.ndarray]) -> Dict[str, dict]:
    """Analyze Shannon entropy of each layer's weight tensor.

    Parameters
    ----------
    weights : dict[str, np.ndarray]
        Mapping of layer name to weight tensor.

    Returns
    -------
    dict[str, dict]
        Per-layer results with keys: entropy, lsb_entropy, is_anomaly.
    """
    results: Dict[str, dict] = {}
    entropies: list[float] = []

    # First pass: compute entropies for all valid layers
    layer_data: Dict[str, tuple] = {}
    for layer_name, tensor in weights.items():
        try:
            flat = tensor.flatten()
            if flat.size < MIN_ELEMENTS:
                logger.warning(
                    "Layer '%s' has fewer than %d elements, skipping.",
                    layer_name, MIN_ELEMENTS,
                )
                continue

            # Sanitize: replace NaN/inf with zero
            flat = np.where(np.isfinite(flat), flat, 0.0)

            byte_array = np.frombuffer(
                flat.astype(np.float32).tobytes(), dtype=np.uint8
            )

            full_entropy = _shannon_entropy(byte_array)
            lsb_bytes = _extract_lsb_bytes(byte_array)
            lsb_entropy = _shannon_entropy(lsb_bytes)

            layer_data[layer_name] = (full_entropy, lsb_entropy)
            entropies.append(full_entropy)

        except Exception:
            logger.warning(
                "Failed to compute entropy for layer '%s'.", layer_name,
                exc_info=True,
            )
            results[layer_name] = {
                "entropy": 0.0,
                "lsb_entropy": 0.0,
                "is_anomaly": False,
            }

    # Compute model-wide mean and std for full entropy
    if entropies:
        mean_entropy = float(np.mean(entropies))
        std_entropy = float(np.std(entropies))
    else:
        mean_entropy = 0.0
        std_entropy = 0.0

    # Second pass: determine anomalies
    for layer_name, (full_entropy, lsb_entropy) in layer_data.items():
        lsb_anomaly = lsb_entropy > LSB_ENTROPY_THRESHOLD

        if std_entropy > 0:
            deviation_anomaly = (
                abs(full_entropy - mean_entropy) > SIGMA_THRESHOLD * std_entropy
            )
        else:
            # All layers have identical entropy; no deviation possible
            deviation_anomaly = False

        is_anomaly = lsb_anomaly or deviation_anomaly

        results[layer_name] = {
            "entropy": round(full_entropy, 6),
            "lsb_entropy": round(lsb_entropy, 6),
            "is_anomaly": bool(is_anomaly),
        }

    return results
