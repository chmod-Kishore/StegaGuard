"""Composite risk scoring for StegaGuard scan results."""

from __future__ import annotations

from models.scan import (
    LayerResult,
    ModelMetadata,
    RiskBreakdown,
    RiskVerdict,
)


# ── per-layer sub-score helpers ──────────────────────────────────────


def _entropy_score(layer: LayerResult) -> float:
    """Normalized entropy score for a single layer."""
    return min(max((layer.lsb_entropy - 5.0) / 3.0, 0.0), 1.0)


def _lsb_score(layer: LayerResult) -> float:
    """Normalized LSB chi-squared score for a single layer."""
    if layer.chi2_p_value < 0.05:
        return min(max(1.0 - layer.chi2_p_value, 0.0), 1.0)
    return 0.0


def _distribution_score(layer: LayerResult) -> float:
    """Normalized KS-statistic score for a single layer."""
    return min(max(layer.ks_statistic * 2.0, 0.0), 1.0)


def _metadata_score(metadata: ModelMetadata) -> float:
    """Score based on file format risk (pickle deserialization)."""
    if metadata.format == "pytorch":
        return 0.5
    return 0.0


# ── layer status classification ──────────────────────────────────────


def _classify_layer(layer: LayerResult) -> str:
    """Return 'normal', 'warning', or 'critical' for a single layer."""
    combined = (
        0.40 * _entropy_score(layer)
        + 0.30 * _lsb_score(layer)
        + 0.30 * _distribution_score(layer)
    )
    if combined >= 0.75:
        return "critical"
    if combined >= 0.40:
        return "warning"
    return "normal"


# ── verdict mapping ──────────────────────────────────────────────────


def _verdict_from_score(score: float) -> RiskVerdict:
    """Map a 0-100 risk score to a RiskVerdict enum value."""
    if score >= 75.0:
        return RiskVerdict.CRITICAL
    if score >= 50.0:
        return RiskVerdict.WARNING
    if score >= 25.0:
        return RiskVerdict.LOW
    return RiskVerdict.CLEAR


# ── public API ────────────────────────────────────────────────────────


def compute_risk(
    layers: list[LayerResult],
    metadata: ModelMetadata,
) -> tuple[float, RiskVerdict, RiskBreakdown, list[LayerResult]]:
    """Score the scan results and return (score, verdict, breakdown, updated_layers).

    The *layers* list is returned with each element's ``status`` field set
    according to its per-layer combined risk.

    Risk formula (weights sum to 1.0):
        0.30 * max(entropy_scores)
      + 0.25 * max(lsb_scores)
      + 0.25 * max(distribution_scores)
      + 0.10 * mean(entropy_scores)
      + 0.10 * metadata_score
    """
    if not layers:
        breakdown = RiskBreakdown(metadata_score=_metadata_score(metadata))
        score = breakdown.metadata_score * 0.10 * 100.0
        return score, _verdict_from_score(score), breakdown, layers

    entropy_scores = [_entropy_score(lr) for lr in layers]
    lsb_scores = [_lsb_score(lr) for lr in layers]
    distribution_scores = [_distribution_score(lr) for lr in layers]
    meta_score = _metadata_score(metadata)

    max_entropy = max(entropy_scores)
    max_lsb = max(lsb_scores)
    max_dist = max(distribution_scores)
    mean_entropy = sum(entropy_scores) / len(entropy_scores)

    raw = (
        0.30 * max_entropy
        + 0.25 * max_lsb
        + 0.25 * max_dist
        + 0.10 * mean_entropy
        + 0.10 * meta_score
    )

    # Scale to 0-100.
    score = round(min(max(raw * 100.0, 0.0), 100.0), 2)

    breakdown = RiskBreakdown(
        max_entropy_score=round(max_entropy, 4),
        max_lsb_score=round(max_lsb, 4),
        max_distribution_score=round(max_dist, 4),
        mean_entropy_score=round(mean_entropy, 4),
        metadata_score=round(meta_score, 4),
    )

    # Update per-layer status and anomaly flags.
    updated_layers: list[LayerResult] = []
    for layer, e_s, l_s, d_s in zip(layers, entropy_scores, lsb_scores, distribution_scores):
        layer = layer.model_copy(
            update={
                "status": _classify_layer(layer),
                "entropy_anomaly": e_s > 0.5,
                "lsb_anomaly": l_s > 0.5,
                "distribution_anomaly": d_s > 0.5,
            }
        )
        updated_layers.append(layer)

    verdict = _verdict_from_score(score)
    return score, verdict, breakdown, updated_layers
