import math
from datetime import datetime
from typing import Optional

class TemporalEvaluator:
    """
    Computes task-conditioned freshness scores for context items.
    For 'strict_recent' tasks (e.g. today's meetings): exponential decay penalizes older items.
    For 'historical_ok' tasks (e.g. how did I meet X): older items receive minimal or zero penalty.
    """

    REFERENCE_DATE = datetime(2026, 9, 20, 12, 0, 0)

    @classmethod
    def score_freshness(cls, timestamp_str: str, preference: str = "balanced") -> float:
        if not timestamp_str:
            return 0.5

        try:
            # Parse ISO or YYYY-MM-DD
            clean_ts = timestamp_str.replace("Z", "").split("T")[0]
            dt = datetime.strptime(clean_ts, "%Y-%m-%d")
        except Exception:
            return 0.6

        days_diff = max(0, (cls.REFERENCE_DATE - dt).days)

        if preference == "strict_recent":
            # Rapid decay: halflife = 7 days
            return max(0.1, round(math.exp(-days_diff / 7.0), 3))
        elif preference == "historical_ok":
            # Very gentle decay: halflife = 365 days
            return max(0.4, round(math.exp(-days_diff / 365.0), 3))
        else: # "balanced"
            # Halflife = 30 days
            return max(0.2, round(math.exp(-days_diff / 30.0), 3))
