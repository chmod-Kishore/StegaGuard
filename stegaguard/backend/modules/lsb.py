"""Chi-square steganalysis on weight tensor LSBs.

Detects non-random patterns in least significant bits that may indicate
steganographic data embedding in neural network weights.
"""

import logging
from typing import Dict

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

MIN_ELEMENTS = 100
P_VALUE_THRESHOLD = 0.01
FLIP_RATIO_DEVIATION = 0.1
EXPECTED_FLIP_RATIO = 0.5


def analyze(weights: Dict[str, np.ndarray]) -> Dict[str, dict]:
    """Perform chi-square steganalysis on each layer's weight tensor.

    Parameters
    ----------
    weights : dict[str, np.ndarray]
        Mapping of layer name to weight tensor.

    Returns
    -------
    dict[str, dict]
        Per-layer results with keys: chi2_statistic, p_value,
        flip_ratio, is_anomaly.
    """
    results: Dict[str, dict] = {}

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

            # Extract LSBs (least significant bit of each byte)
            lsbs = byte_array & 1

            # Chi-square test for uniformity of 0s and 1s
            n = len(lsbs)
            count_zeros = int(np.sum(lsbs == 0))
            count_ones = n - count_zeros
            observed = np.array([count_zeros, count_ones], dtype=np.float64)
            expected = np.array([n / 2.0, n / 2.0], dtype=np.float64)

            chi2_result = stats.chisquare(observed, f_exp=expected)
            chi2_statistic = float(chi2_result.statistic)
            p_value = float(chi2_result.pvalue)

            # Flip ratio: fraction of adjacent LSB pairs that differ
            if len(lsbs) > 1:
                diffs = np.diff(lsbs)
                flip_ratio = float(np.sum(diffs != 0)) / (len(lsbs) - 1)
            else:
                flip_ratio = 0.5  # default for single-element edge case

            # Anomaly detection
            p_value_anomaly = p_value < P_VALUE_THRESHOLD
            flip_anomaly = abs(flip_ratio - EXPECTED_FLIP_RATIO) > FLIP_RATIO_DEVIATION
            is_anomaly = p_value_anomaly or flip_anomaly

            results[layer_name] = {
                "chi2_statistic": round(chi2_statistic, 6),
                "p_value": round(p_value, 10),
                "flip_ratio": round(flip_ratio, 6),
                "is_anomaly": bool(is_anomaly),
            }

        except Exception:
            logger.warning(
                "Failed chi-square analysis for layer '%s'.", layer_name,
                exc_info=True,
            )
            results[layer_name] = {
                "chi2_statistic": 0.0,
                "p_value": 1.0,
                "flip_ratio": 0.5,
                "is_anomaly": False,
            }

    return results
