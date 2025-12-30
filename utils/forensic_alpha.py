import pandas as pd
import numpy as np


# -------------------------------------------------
# Robust Z-score (expanding window, no look-ahead)
# -------------------------------------------------
def rolling_zscore(series: pd.Series) -> pd.Series:
    z = []

    for i in range(len(series)):
        window = series.iloc[: i + 1]

        if window.count() < 2 or window.std() == 0:
            z.append(0.0)
        else:
            z.append((window.iloc[-1] - window.mean()) / window.std())

    return pd.Series(z, index=series.index)


# -------------------------------------------------
# Main: Forensic Alpha Calculator (Robust)
# -------------------------------------------------
def forensic_alpha(
    beneish: pd.Series,
    sloan: pd.Series,
    piotroski: pd.Series,
    altman: pd.Series,
    min_signals: int = 3
) -> pd.DataFrame:
    """
    Computes year-wise forensic alpha using robust normalization.

    Design guarantees:
    - No look-ahead bias
    - No silent re-weighting
    - Sensitivity-safe
    """

    df = pd.DataFrame({
        "beneish": beneish,
        "sloan": sloan,
        "piotroski": piotroski,
        "altman": altman
    })

    # Require minimum signals per year
    df["signal_count"] = df.notna().sum(axis=1)
    df = df[df["signal_count"] >= min_signals]

    if df.empty:
        return pd.DataFrame()

    # -------------------------------------------------
    # Direction-aware normalization
    # -------------------------------------------------
    signals = pd.DataFrame({
        "beneish_signal": -rolling_zscore(df["beneish"]),
        "sloan_signal": -rolling_zscore(df["sloan"]),
        "piotroski_signal": rolling_zscore(df["piotroski"]),
        "altman_signal": rolling_zscore(df["altman"])
    })

    # -------------------------------------------------
    # Weights (interpretable & defensible)
    # -------------------------------------------------
    base_weights = {
        "beneish_signal": 0.35,
        "sloan_signal": 0.25,
        "piotroski_signal": 0.25,
        "altman_signal": 0.15
    }

    weights = pd.Series(base_weights)

    # -------------------------------------------------
    # Dynamic normalization to avoid silent re-weighting
    # -------------------------------------------------
    weighted = signals.mul(weights)

    normalized_weights = weighted.notna().mul(weights).sum(axis=1)

    forensic_alpha = weighted.sum(axis=1) / normalized_weights.replace(0, np.nan)

    # -------------------------------------------------
    # Final output
    # -------------------------------------------------
    result = signals.copy()
    result["forensic_alpha"] = forensic_alpha.round(4)
    result["signal_count"] = df["signal_count"]

    # -------------------------------------------------
    # Qualitative interpretation
    # -------------------------------------------------
    def label(alpha):
        if alpha > 1.0:
            return "Strong Positive"
        elif alpha > 0.3:
            return "Positive"
        elif alpha < -1.0:
            return "Strong Negative"
        elif alpha < -0.3:
            return "Negative"
        else:
            return "Neutral"

    result["signal"] = result["forensic_alpha"].apply(label)

    return result
