import os
from typing import Iterable


def _get_env_list(name: str, default: Iterable[str]) -> list[str]:
    value = os.getenv(name)
    if not value:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


MONGO_URI = os.getenv("NECTA_MONGO_URI", "mongodb://root:admin@localhost:27018/")
DB_NAME = os.getenv("NECTA_DB_NAME", "necta")

SCHEDULER_ENABLED = os.getenv("NECTA_SCHEDULER_ENABLED", "false").lower() == "true"
SCHEDULER_INTERVAL_SECONDS = int(os.getenv("NECTA_SCHEDULER_INTERVAL_SECONDS", "3600"))
SCHEDULER_EXAM_TYPES = _get_env_list("NECTA_SCHEDULER_EXAM_TYPES", ["ACSEE", "CSEE"])
SCHEDULER_YEARS = [int(year) for year in _get_env_list("NECTA_SCHEDULER_YEARS", [])]
SCHEDULER_SOURCE_URL = os.getenv("NECTA_SCHEDULER_SOURCE_URL", "https://maktaba.tetea.org/exam-results/")

EXPORT_DIR = os.getenv("NECTA_EXPORT_DIR", "resource/csv")
JOB_LOCK_MINUTES = int(os.getenv("NECTA_JOB_LOCK_MINUTES", "30"))

# ---------------------------------------------------------------------------
# Division weight coefficients for pass-rate / ranking computation.
# Higher weight = higher quality.  Div 0 and non-pass categories get 0.
# Formula:  passRate = (w1×divI + w2×divII + w3×divIII + w4×divIV) / (w1 × total)
# ---------------------------------------------------------------------------
DIVISION_WEIGHT_I = int(os.getenv("NECTA_DIVISION_WEIGHT_I", "4"))
DIVISION_WEIGHT_II = int(os.getenv("NECTA_DIVISION_WEIGHT_II", "3"))
DIVISION_WEIGHT_III = int(os.getenv("NECTA_DIVISION_WEIGHT_III", "2"))
DIVISION_WEIGHT_IV = int(os.getenv("NECTA_DIVISION_WEIGHT_IV", "1"))

DIVISION_WEIGHTS: dict[str, int] = {
    "I": DIVISION_WEIGHT_I,
    "II": DIVISION_WEIGHT_II,
    "III": DIVISION_WEIGHT_III,
    "IV": DIVISION_WEIGHT_IV,
}

# ---------------------------------------------------------------------------
# Rank-score blending factor (0.0–1.0).
# rankScore = α × passRate + (1 - α) × normalisedSchoolSize
# Higher α = pass rate dominates; lower α = school size matters more.
# ---------------------------------------------------------------------------
PASS_RATE_ALPHA = float(os.getenv("NECTA_PASS_RATE_ALPHA", "0.85"))

