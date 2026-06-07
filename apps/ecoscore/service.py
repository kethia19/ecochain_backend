"""
EcoChain Housing — EcoScore Service
=====================================
File:    apps/ecoscore/service.py
Dataset: data/ecoscore/EcoScore_WestAfrica_Hackathon_Master.xlsx

Sheets used:
  EcoScore_Formula        — category weights (Category, Weight)
  WestAfrica_Plants       — plant CO₂ absorption (plant name, CO₂ kg/yr col)
  Sustainable_Materials   — material sustainability scores
  Renewable_Energy        — energy system CO₂ reduction factors
  Water_Conservation      — water action scores
  Waste_Management        — waste action scores
  Maintenance_Actions     — maintenance action scores
  Ratings                 — score → rating band (Range, Rating)
  Badges                  — badge definitions (Badge, Requirement)

Output:
  {ecoScore, ratingBand, carbonReductionKg, earnedBadges, breakdown}
"""

import logging
import os
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

_ECO_FILE = os.environ.get(
    "ECOSCORE_DATA_PATH",
    str(_DATA_DIR / "ecoscore" / "EcoScore_WestAfrica_Hackathon_Master.xlsx"),
)

# ──────────────────────────────────────────────────────────────────────────────
# Load all sheets once at startup
# ──────────────────────────────────────────────────────────────────────────────

try:
    _xls              = pd.ExcelFile(_ECO_FILE)
    _ECO_FORMULA      = pd.read_excel(_xls, "EcoScore_Formula")
    _PLANTS_DF        = pd.read_excel(_xls, "WestAfrica_Plants")
    _MATERIALS_DF     = pd.read_excel(_xls, "Sustainable_Materials")
    _ENERGY_DF        = pd.read_excel(_xls, "Renewable_Energy")
    _WATER_DF         = pd.read_excel(_xls, "Water_Conservation")
    _WASTE_DF         = pd.read_excel(_xls, "Waste_Management")
    _MAINT_ACTIONS_DF = pd.read_excel(_xls, "Maintenance_Actions")
    _RATINGS_DF       = pd.read_excel(_xls, "Ratings")
    _BADGES_DF        = pd.read_excel(_xls, "Badges")
    logger.info("EcoScore master dataset loaded (%d formula rows)", len(_ECO_FORMULA))
except Exception as exc:
    _xls = None
    _ECO_FORMULA = _PLANTS_DF = _MATERIALS_DF = _ENERGY_DF = pd.DataFrame()
    _WATER_DF = _WASTE_DF = _MAINT_ACTIONS_DF = _RATINGS_DF = _BADGES_DF = pd.DataFrame()
    logger.error("Could not load EcoScore dataset: %s", exc)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _col(df: pd.DataFrame, *keywords: str) -> str | None:
    """Return the first column whose lowercased name contains any keyword."""
    for kw in keywords:
        match = next((c for c in df.columns if kw in c.lower()), None)
        if match:
            return match
    return None


def _get_rating(score: float) -> str:
    for _, row in _RATINGS_DF.iterrows():
        try:
            lo, hi = map(int, str(row["Range"]).split("-"))
            if lo <= score <= hi:
                return str(row["Rating"])
        except (ValueError, KeyError):
            continue
    return "Needs Improvement"


def _get_badges(house_data: dict, ecoscore: float) -> list:
    earned = []
    if house_data.get("plants") or house_data.get("trees_planted", 0) >= 100:
        earned.append("Tree Champion")
    if house_data.get("renewable_systems"):
        earned.append("Solar Hero")
    if house_data.get("water_actions") or house_data.get("water_savings_percent", 0) >= 20:
        earned.append("Water Guardian")
    if house_data.get("waste_actions") or house_data.get("waste_recycled_percent", 0) >= 50:
        earned.append("Recycling Star")
    if ecoscore >= 90:
        earned.append("Eco Leader")
    return earned


# ──────────────────────────────────────────────────────────────────────────────
# Per-category score calculators
# ──────────────────────────────────────────────────────────────────────────────

def _score_plants(plants: list) -> tuple[float, float]:
    """Returns (score_0_to_100, carbon_kg_per_year)."""
    if not plants or _PLANTS_DF.empty:
        return 0.0, 0.0
    c_plant = _col(_PLANTS_DF, "plant")
    c_co2   = _col(_PLANTS_DF, "co2")
    if not c_plant or not c_co2:
        return 0.0, 0.0
    matched    = _PLANTS_DF[_PLANTS_DF[c_plant].isin(plants)]
    total_co2  = float(matched[c_co2].sum())
    max_co2    = float(_PLANTS_DF[c_co2].max()) * 5
    score      = min(100.0, (total_co2 / max_co2) * 100) if max_co2 > 0 else 0.0
    return score, total_co2


def _score_materials(materials: list) -> float:
    if not materials or _MATERIALS_DF.empty:
        return 0.0
    c_mat   = _col(_MATERIALS_DF, "material")
    c_score = _col(_MATERIALS_DF, "score")
    if not c_mat or not c_score:
        return 0.0
    avg = _MATERIALS_DF[_MATERIALS_DF[c_mat].isin(materials)][c_score].mean()
    return 0.0 if pd.isna(avg) else float(avg)


def _score_energy(systems: dict) -> tuple[float, float]:
    """Returns (score_0_to_100, avoided_co2_kg_per_year)."""
    if not systems or _ENERGY_DF.empty:
        return 0.0, 0.0
    c_sys = _col(_ENERGY_DF, "system")
    c_red = _col(_ENERGY_DF, "reduction")
    if not c_sys or not c_red:
        return 0.0, 0.0
    total = sum(
        float(_ENERGY_DF[_ENERGY_DF[c_sys].str.contains(sys, case=False, na=False)][c_red].sum()) * count
        for sys, count in systems.items()
    )
    score = min(100.0, (total / 5000.0) * 100)
    return score, total


def _score_list_actions(df: pd.DataFrame, actions: list) -> float:
    if not actions or df.empty:
        return 0.0
    c_act   = _col(df, "action")
    c_score = _col(df, "score")
    if not c_act or not c_score:
        return 0.0
    return min(100.0, float(df[df[c_act].isin(actions)][c_score].sum()))


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def calculate_ecoscore(house_data: dict) -> dict:
    """
    Calculate the EcoScore for a property.

    Parameters (all keys lowercase, all optional — defaults to 0 / empty list)
    ----------
    house_data : {
        "plants":               ["Neem", "Mahogany", "Teak"],
        "materials":            ["Bamboo", "Rammed Earth"],
        "renewable_systems":    {"Solar": 1},
        "water_actions":        ["Rainwater Harvesting", "Low Flow Fixtures"],
        "waste_actions":        ["Recycling Program", "Composting"],
        "maintenance_actions":  ["Energy Audit", "Smart Monitoring"],
        # optional for badge checks:
        "trees_planted":        0,
        "water_savings_percent":  0.0,
        "waste_recycled_percent": 0.0,
    }

    Returns
    -------
    {
        "ecoScore":           int (0–100),
        "ratingBand":         str ("Platinum" | "Gold" | "Silver" | "Bronze" | "Needs Improvement"),
        "carbonReductionKg":  float (estimated annual CO₂ avoided, kg/year),
        "earnedBadges":       list[str],
        "breakdown": {
            "Plants & Green Spaces":  float,
            "Building Materials":     float,
            "Renewable Energy":       float,
            "Water Conservation":     float,
            "Waste Management":       float,
            "Maintenance Actions":    float,
        }
    }
    """
    if _ECO_FORMULA.empty:
        raise RuntimeError(
            "EcoScore dataset not loaded. Set ECOSCORE_DATA_PATH env var or place the "
            "file at data/ecoscore/EcoScore_WestAfrica_Hackathon_Master.xlsx."
        )

    plants    = house_data.get("plants", [])
    materials = house_data.get("materials", [])
    systems   = house_data.get("renewable_systems", {})
    water_act = house_data.get("water_actions", [])
    waste_act = house_data.get("waste_actions", [])
    maint_act = house_data.get("maintenance_actions", [])

    # Raw scores per category
    plant_score,  plant_co2   = _score_plants(plants)
    energy_score, energy_co2  = _score_energy(systems)
    mat_score    = _score_materials(materials)
    water_score  = _score_list_actions(_WATER_DF,         water_act)
    waste_score  = _score_list_actions(_WASTE_DF,         waste_act)
    maint_score  = _score_list_actions(_MAINT_ACTIONS_DF, maint_act)

    raw_scores = {
        "Plants & Green Spaces": plant_score,
        "Building Materials":    mat_score,
        "Renewable Energy":      energy_score,
        "Water Conservation":    water_score,
        "Waste Management":      waste_score,
        "Maintenance Actions":   maint_score,
    }

    # Apply weights from the EcoScore_Formula sheet
    weights   = _ECO_FORMULA.set_index("Category")["Weight"].astype(float).to_dict()
    total     = 0.0
    breakdown = {}
    for category, weight in weights.items():
        contribution = raw_scores.get(category, 0.0) * (weight / 100.0)
        breakdown[category] = round(contribution, 1)
        total += contribution

    final_score      = min(100, max(0, int(total)))
    carbon_kg        = round(plant_co2 + energy_co2, 2)

    return {
        "ecoScore":          final_score,
        "ratingBand":        _get_rating(final_score),
        "carbonReductionKg": carbon_kg,
        "earnedBadges":      _get_badges(house_data, final_score),
        "breakdown":         breakdown,
    }
