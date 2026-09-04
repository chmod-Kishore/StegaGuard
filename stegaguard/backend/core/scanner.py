"""Scan orchestrator — runs analysis modules and assembles the final ScanResult."""

from __future__ import annotations

import asyncio
import traceback
from typing import Awaitable, Callable, Optional

import numpy as np

from models.scan import (
    LayerResult,
    ModelMetadata,
    RiskVerdict,
    ScanProgress,
    ScanResult,
    ScanStatus,
)
from core.risk_scorer import compute_risk

# Type alias for the optional async progress callback.
ProgressCallback = Optional[Callable[[ScanProgress], Awaitable[None]]]


async def _emit(
    callback: ProgressCallback,
    scan_id: str,
    stage: str,
    progress: float,
    message: str = "",
    layer: str = "",
) -> None:
    """Fire a progress event if a callback is registered."""
    if callback is not None:
        event = ScanProgress(
            scan_id=scan_id,
            stage=stage,
            layer=layer,
            progress=progress,
            message=message,
        )
        await callback(event)


def _run_module_sync(
    module_name: str,
    weights: dict[str, np.ndarray],
) -> dict[str, dict]:
    """Import and call one analysis module, returning its per-layer dict.

    Each module exposes: ``analyze(weights) -> dict[str, dict]``
    """
    if module_name == "entropy":
        from modules import entropy as mod
    elif module_name == "lsb":
        from modules import lsb as mod
    elif module_name == "distribution":
        from modules import distribution as mod
    else:
        raise ValueError(f"Unknown analysis module: {module_name}")

    return mod.analyze(weights)


async def run_scan(
    weights: dict[str, np.ndarray],
    metadata: ModelMetadata,
    progress_callback: ProgressCallback = None,
) -> ScanResult:
    """Run a full StegaGuard scan and return the completed ScanResult.

    Parameters
    ----------
    weights:
        Mapping of layer names to numpy weight arrays (pre-filtered).
    metadata:
        Parsed model metadata.
    progress_callback:
        Optional async callable that receives ``ScanProgress`` events as
        the scan advances through its stages.
    """
    result = ScanResult(status=ScanStatus.RUNNING, metadata=metadata)
    scan_id = result.scan_id

    try:
        layer_names = list(weights.keys())

        # ── Stage 1: Entropy analysis ────────────────────────────────
        await _emit(
            progress_callback, scan_id, "entropy", 0.0, "Starting entropy analysis"
        )
        entropy_results = await asyncio.to_thread(_run_module_sync, "entropy", weights)
        await _emit(
            progress_callback, scan_id, "entropy", 1.0, "Entropy analysis complete"
        )

        # ── Stage 2: LSB analysis ────────────────────────────────────
        await _emit(
            progress_callback, scan_id, "lsb", 0.0, "Starting LSB analysis"
        )
        lsb_results = await asyncio.to_thread(_run_module_sync, "lsb", weights)
        await _emit(
            progress_callback, scan_id, "lsb", 1.0, "LSB analysis complete"
        )

        # ── Stage 3: Distribution analysis ───────────────────────────
        await _emit(
            progress_callback,
            scan_id,
            "distribution",
            0.0,
            "Starting distribution analysis",
        )
        distribution_results = await asyncio.to_thread(
            _run_module_sync, "distribution", weights
        )
        await _emit(
            progress_callback,
            scan_id,
            "distribution",
            1.0,
            "Distribution analysis complete",
        )

        # ── Aggregate per-layer results ──────────────────────────────
        layer_results: list[LayerResult] = []
        for name in layer_names:
            e = entropy_results.get(name, {})
            l = lsb_results.get(name, {})
            d = distribution_results.get(name, {})

            layer_results.append(
                LayerResult(
                    name=name,
                    param_count=int(weights[name].size),
                    entropy=float(e.get("entropy", 0.0)),
                    lsb_entropy=float(e.get("lsb_entropy", 0.0)),
                    chi2_statistic=float(l.get("chi2_statistic", 0.0)),
                    chi2_p_value=float(l.get("chi2_p_value", 1.0)),
                    flip_ratio=float(l.get("flip_ratio", 0.5)),
                    ks_statistic=float(d.get("ks_statistic", 0.0)),
                    ks_p_value=float(d.get("ks_p_value", 1.0)),
                    kurtosis=float(d.get("kurtosis", 0.0)),
                )
            )

        # ── Stage 4: Scoring ─────────────────────────────────────────
        await _emit(
            progress_callback, scan_id, "scoring", 0.0, "Computing risk score"
        )
        score, verdict, breakdown, updated_layers = compute_risk(
            layer_results, metadata
        )
        await _emit(
            progress_callback, scan_id, "scoring", 1.0, "Scoring complete"
        )

        # ── Assemble final result ────────────────────────────────────
        anomalous = sum(1 for lr in updated_layers if lr.status != "normal")
        summary = (
            f"Scanned {metadata.filename} ({metadata.format}): "
            f"{metadata.layer_count} layers, {metadata.total_params:,} parameters. "
            f"Risk score {score}/100 ({verdict.value}). "
            f"{anomalous} layer(s) flagged."
        )

        result = result.model_copy(
            update={
                "status": ScanStatus.COMPLETED,
                "risk_score": score,
                "verdict": verdict,
                "risk_breakdown": breakdown,
                "layer_results": updated_layers,
                "summary": summary,
            }
        )

    except Exception as exc:
        result = result.model_copy(
            update={
                "status": ScanStatus.FAILED,
                "error": f"{type(exc).__name__}: {exc}",
                "summary": f"Scan failed: {exc}",
            }
        )

    return result
