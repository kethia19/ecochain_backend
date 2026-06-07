"""
EcoChain Housing — Green Match ML Service
==========================================
Team:    AI/ML (Group 15)
File:    apps/ai_engine/ml_service.py
Dataset: data/plants/EastAfricaRegionCleaned.xlsx

Django endpoint: POST /api/v1/green-match/

Setup
-----
Add to .env (only needed to override the default path):
    PLANT_DATA_PATH=/abs/path/to/data/plants/EastAfricaRegionCleaned.xlsx

Install:
    pip install scikit-learn pandas openpyxl numpy
"""

import logging
import os
from pathlib import Path
import warnings

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

DATA_PATH = os.environ.get(
    "PLANT_DATA_PATH",
    str(_DATA_DIR / "plants" / "EastAfricaRegionCleaned.xlsx"),
)

FEATURES = [
    "climate_zone", "sun_exposure", "soil_type", "water_need",
    "drought_tolerance", "growth_rate", "maintenance_level", "plant_type",
]
TARGET = "common_name"

ORDINAL_COLS = ["water_need", "drought_tolerance", "growth_rate", "maintenance_level"]
ORDINAL_CATS = [
    ["Unknown", "Very Low", "Low", "Moderate", "High", "Very High"],
    ["Unknown", "Low", "Medium", "High", "Very High"],
    ["Unknown", "Very Slow", "Slow", "Moderate", "Fast", "Very Fast"],
    ["Unknown", "Very Low", "Low", "Medium", "High"],
]
NOMINAL_COLS = ["climate_zone", "sun_exposure", "soil_type", "plant_type"]

# ---------------------------------------------------------------------------
# Model — trained once at import, cached in memory
# ---------------------------------------------------------------------------
_pipeline: Pipeline | None = None
_label_enc: LabelEncoder | None = None


def _train():
    global _pipeline, _label_enc

    df = pd.read_excel(DATA_PATH)
    df["soil_type"]    = df["soil_type"].str.strip().str.lower()
    df["climate_zone"] = df["climate_zone"].str.strip()
    df = df.fillna("Unknown")

    X = df[FEATURES]
    _label_enc = LabelEncoder()
    y = _label_enc.fit_transform(df[TARGET])

    preprocessor = ColumnTransformer([
        ("ord", OrdinalEncoder(
            categories=ORDINAL_CATS,
            handle_unknown="use_encoded_value",
            unknown_value=-1,
        ), ORDINAL_COLS),
        ("nom", OrdinalEncoder(
            handle_unknown="use_encoded_value",
            unknown_value=-1,
        ), NOMINAL_COLS),
    ])

    clf = RandomForestClassifier(
        n_estimators=300, max_depth=None, min_samples_leaf=1,
        class_weight="balanced", random_state=42, n_jobs=-1,
    )
    _pipeline = Pipeline([("pre", preprocessor), ("clf", clf)])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    _pipeline.fit(X_train, y_train)
    acc = accuracy_score(y_test, _pipeline.predict(X_test))
    logger.info("Plant ML model trained — accuracy: %.1f%%", acc * 100)


try:
    _train()
except Exception as exc:
    logger.error("Could not train plant model: %s", exc)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def predict_plants(
    climate_zone: str,
    sun_exposure: str,
    soil_type: str,
    water_need: str,
    drought_tolerance: str = "Medium",
    growth_rate: str = "Moderate",
    maintenance_level: str = "Low",
    plant_type: str = "Unknown",
    top_n: int = 10,
) -> list[dict]:
    """
    Return ranked plant predictions for the given growing conditions.

    Returns
    -------
    [{"plant_name": str, "confidence": float, "match_score": int}]
    """
    if _pipeline is None or _label_enc is None:
        raise RuntimeError("ML model not loaded. Check PLANT_DATA_PATH and logs.")

    row = pd.DataFrame([{
        "climate_zone":      climate_zone,
        "sun_exposure":      sun_exposure,
        "soil_type":         soil_type.strip().lower(),
        "water_need":        water_need,
        "drought_tolerance": drought_tolerance,
        "growth_rate":       growth_rate,
        "maintenance_level": maintenance_level,
        "plant_type":        plant_type,
    }])

    proba   = _pipeline.predict_proba(row)[0]
    results = sorted(zip(_label_enc.classes_, proba), key=lambda x: x[1], reverse=True)

    return [
        {
            "plant_name":  name,
            "confidence":  round(float(prob), 4),
            "match_score": round(float(prob) * 100),
        }
        for name, prob in results[:top_n]
        if prob > 0
    ]


def model_is_ready() -> bool:
    return _pipeline is not None and _label_enc is not None


# ---------------------------------------------------------------------------
# Quick test — python ml_service.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    results = predict_plants(
        climate_zone="Highland", sun_exposure="Full Sun",
        soil_type="Loamy", water_need="Moderate",
        growth_rate="Fast", plant_type="Tree", top_n=5,
    )
    print("Top 5 — Highland | Full Sun | Loamy | Tree")
    print("-" * 45)
    for r in results:
        bar = "█" * r["match_score"] + "░" * (100 - r["match_score"])
        print(f"  {r['plant_name']:<30} {r['match_score']:>3}%  {bar[:28]}")
    print("\n✅  ml_service.py working correctly.")
