"""Distribution deviation analysis for weight tensors.

Compares observed weight distributions against theoretically expected
initializations (Kaiming, Xavier) and flags anomalies via the
Kolmogorov-Smirnov test and excess kurtosis.
"""

import logging
from typing import Dict

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

MIN_ELEMENTS = 100
SUBSAMPLE_SIZE = 10000
P_VALUE_THRESHOLD = 0.01
KURTOSIS_THRESHOLD = 4.0


def _infer_expected_std(layer_name: str, shape: tuple) -> float:
    """Infer the expected standard deviation from layer name and shape.

    - Conv layers (ndim >= 4): Kaiming normal, std = sqrt(2 / fan_in)
    - FC/Linear layers (2D): Xavier normal, std = sqrt(2 / (fan_in + fan_out))
    - Otherwise: returns 0.0 to signal self-comparison mode.
    """
    name_lower = layer_name.lower()
    ndim = len(shape)

    if ("conv" in name_lower or "weight" in name_lower) and ndim >= 4:
        # Kaiming: fan_in = product of shape[1:]
        fan_in = int(np.prod(shape[1:]))
        if fan_in > 0:
            return float(np.sqrt(2.0 / fan_in))

    if "fc" in name_lower or "linear" in name_lower or ndim == 2:
        # Xavier: fan_in = shape[1], fan_out = shape[0]
        if ndim >= 2 and shape[0] > 0 and shape[1] > 0:
            fan_in = shape[1]
            fan_out = shape[0]
            return float(np.sqrt(2.0 / (fan_in + fan_out)))

    return 0.0


def analyze(weights: Dict[str, np.ndarray]) -> Dict[str, dict]:
    """Analyze distribution deviation of each layer's weight tensor.

    Parameters
    ----------
    weights : dict[str, np.ndarray]
        Mapping of layer name to weight tensor.

    Returns
    -------
    dict[str, dict]
        Per-layer results with keys: ks_statistic, p_value,
        kurtosis, is_anomaly.
    """
    results: Dict[str, dict] = {}

    for layer_name, tensor in weights.items():
        try:
            flat = tensor.flatten().astype(np.float64)
            if flat.size < MIN_ELEMENTS:
                logger.warning(
                    "Layer '%s' has fewer than %d elements, skipping.",
                    layer_name, MIN_ELEMENTS,
                )
                continue

            # Sanitize: replace NaN/inf with zero
            flat = np.where(np.isfinite(flat), flat, 0.0)

            # Determine expected std
            expected_std = _infer_expected_std(layer_name, tensor.shape)
            if expected_std <= 0:
                # Self-comparison: use the layer's own std
                expected_std = float(np.std(flat))
                if expected_std <= 0:
                    # All values identical; no meaningful distribution test
                    results[layer_name] = {
                        "ks_statistic": 0.0,
                        "p_value": 1.0,
                        "kurtosis": 0.0,
                        "is_anomaly": False,
                    }
                    continue

            # Subsample for large layers
            if flat.size > SUBSAMPLE_SIZE:
                rng = np.random.default_rng(seed=42)
                sample = rng.choice(flat, size=SUBSAMPLE_SIZE, replace=False)
            else:
                sample = flat

            # KS test against normal(0, expected_std)
            # Normalize sample to standard normal, then test against N(0,1)
            # This avoids scipy version issues with args= parameter
            normalized_sample = sample / expected_std
            ks_result = stats.kstest(normalized_sample, "norm")
            ks_statistic = float(ks_result.statistic)
            p_value = float(ks_result.pvalue)

            # Excess kurtosis
            kurt = float(stats.kurtosis(flat))

            # Anomaly detection
            p_value_anomaly = p_value < P_VALUE_THRESHOLD
            kurtosis_anomaly = abs(kurt) > KURTOSIS_THRESHOLD
            is_anomaly = p_value_anomaly or kurtosis_anomaly

            results[layer_name] = {
                "ks_statistic": round(ks_statistic, 6),
                "p_value": round(p_value, 10),
                "kurtosis": round(kurt, 6),
                "is_anomaly": bool(is_anomaly),
            }

        except Exception:
            logger.warning(
                "Failed distribution analysis for layer '%s'.", layer_name,
                exc_info=True,
            )
            results[layer_name] = {
                "ks_statistic": 0.0,
                "p_value": 1.0,
                "kurtosis": 0.0,
                "is_anomaly": False,
            }

    return results
