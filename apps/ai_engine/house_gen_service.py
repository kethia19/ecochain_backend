"""
EcoChain Housing — House Generation Service
=============================================
Team:    AI/ML (Group 15)
File:    apps/ai_engine/house_gen_service.py
Datasets:
    data/housing/Scalable_Eco_Housing_Cost_Model101.xlsx → cost per bedroom
    data/housing/Eco_Housing_Expanded.xlsx               → country materials,
                                                           Labour_Rates sheet,
                                                           Operational_Savings sheet
External APIs:
    Groq  (llama-3.3-70b-versatile) — house description
    Pollinations AI                  — exterior + interior render

Endpoint served:
    POST /api/v1/house/generate
"""

import base64
import logging
import os
import random
import time
from pathlib import Path
from urllib.parse import quote as url_quote

import pandas as pd
import requests
from groq import Groq

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

_GROQ_MODEL = "llama-3.3-70b-versatile"
_groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ──────────────────────────────────────────────────────────────────────────────
# Dataset loading
# ──────────────────────────────────────────────────────────────────────────────

_COST_PATH = os.environ.get(
    "COST_MODEL_PATH",
    str(_DATA_DIR / "housing" / "Scalable_Eco_Housing_Cost_Model101.xlsx"),
)
_HOUSING_PATH = os.environ.get(
    "HOUSING_DATA_PATH",
    str(_DATA_DIR / "housing" / "Eco_Housing_Expanded.xlsx"),
)

try:
    _cost_df = pd.read_excel(_COST_PATH)
    _cost_df.columns = _cost_df.columns.str.strip()
    logger.info("Cost model loaded for house generation (%d rows)", len(_cost_df))
except Exception as exc:
    _cost_df = pd.DataFrame()
    logger.error("Could not load cost model: %s", exc)

try:
    _housing_df = pd.read_excel(_HOUSING_PATH)
    _housing_df.columns = _housing_df.columns.str.strip()
    logger.info("Housing dataset loaded for house generation")
except Exception as exc:
    _housing_df = pd.DataFrame()
    logger.error("Could not load housing dataset: %s", exc)

try:
    _labour_df = pd.read_excel(_HOUSING_PATH, sheet_name="Labour_Rates")
    logger.info("Labour rates sheet loaded")
except Exception as exc:
    _labour_df = pd.DataFrame()
    logger.warning("Labour_Rates sheet not found: %s", exc)

try:
    _operational_df = pd.read_excel(_HOUSING_PATH, sheet_name="Operational_Savings")
    logger.info("Operational savings sheet loaded")
except Exception as exc:
    _operational_df = pd.DataFrame()
    logger.warning("Operational_Savings sheet not found: %s", exc)

# ──────────────────────────────────────────────────────────────────────────────
# Style modifiers (used in image prompts)
# ──────────────────────────────────────────────────────────────────────────────

_STYLE_MODIFIERS = {
    "Traditional": "mud walls, thatched or zinc roof, courtyard layout, local African architecture",
    "Modern":      "concrete, large glass windows, flat roof, sleek modern finish",
    "Minimalist":  "simple geometric shape, clean lines, minimal windows, white exterior",
    "Colonial":    "white walls, veranda with pillars, pitched roof, symmetrical windows",
}

_HOUSE_PROMPT = """\
Design a {bedrooms} bedroom {style} house for {country}, West Africa.
Structure type: {material_type} | Size: {avg_sqft:.0f} sqft
Available eco materials: {material_list}

Provide:
1. A creative, culturally-relevant house name
2. A 2-sentence description highlighting eco features
3. Five architectural features specific to the {style} style in {country}

Respond in plain text. Do not use JSON or markdown."""


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _get_labour_and_op_costs(bedrooms: int, avg_sqft: float) -> tuple[float, float]:
    labour_cost = avg_sqft * 8000  # NGN fallback

    if not _labour_df.empty:
        row = _labour_df[_labour_df.iloc[:, 0] == bedrooms]
        if not row.empty:
            labour_cost = float(row.iloc[0, 1])

    op_cost = 300_000  # NGN fallback
    if not _operational_df.empty:
        row = _operational_df[_operational_df.iloc[:, 0] == bedrooms]
        if not row.empty:
            op_cost = float(row.iloc[0, 1])

    return labour_cost, op_cost


def _generate_image(prompt: str) -> str:
    """Return base64-encoded JPEG string, or empty string on failure."""
    safe_prompt = url_quote(prompt)
    seed = random.randint(1, 9999)
    url  = (
        f"https://image.pollinations.ai/prompt/{safe_prompt}"
        f"?width=1024&height=1024&model=flux&seed={seed}"
    )
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            return base64.b64encode(resp.content).decode("utf-8")
        except requests.exceptions.Timeout:
            logger.warning("Image generation timeout (attempt %d/3)", attempt + 1)
            time.sleep(3)
        except Exception as exc:
            logger.error("Image generation failed: %s", exc)
            break
    return ""


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

VALID_STYLES = list(_STYLE_MODIFIERS.keys())  # exposed so view can validate


def generate_house(style: str, country: str, bedrooms: int) -> dict:
    """
    Generate a full AI house design with cost breakdown and rendered images.

    Parameters
    ----------
    style    : "Traditional" | "Modern" | "Minimalist" | "Colonial"
    country  : e.g. "Nigeria", "Ghana", "Senegal"
    bedrooms : 1–10

    Returns
    -------
    {house_name, style, bedrooms, country, sqft, material_type, description,
     construction_cost, labour_cost, operational_cost, grand_total,
     exterior, interior}
    Costs in NGN (local currency). Images are data-URI strings.
    """
    # ── Cost model lookup ────────────────────────────────────────────────────
    cost_row = (
        _cost_df[_cost_df.iloc[:, 0] == bedrooms]
        if not _cost_df.empty else pd.DataFrame()
    )

    if cost_row.empty:
        avg_sqft      = float(bedrooms * 350)
        cost_per_sqft = 40_000.0
        material_type = "Standard"
        logger.warning("%dBR not in cost model — using estimates", bedrooms)
    else:
        avg_sqft      = float(cost_row.iloc[0, 1])
        cost_per_sqft = float(cost_row.iloc[0, 3])
        material_type = str(cost_row.iloc[0, 2])

    # ── Country materials ────────────────────────────────────────────────────
    material_list = ["Bamboo", "Recycled Steel"]
    if not _housing_df.empty:
        country_rows = _housing_df[_housing_df.iloc[:, 0] == country]
        if not country_rows.empty:
            material_list = country_rows.iloc[:, 1].dropna().tolist()[:5]

    # ── Costs ────────────────────────────────────────────────────────────────
    labour_cost, op_cost = _get_labour_and_op_costs(bedrooms, avg_sqft)
    construction_cost = avg_sqft * cost_per_sqft
    grand_total       = construction_cost + labour_cost + op_cost

    # ── AI description ───────────────────────────────────────────────────────
    prompt = _HOUSE_PROMPT.format(
        bedrooms=bedrooms,
        style=style,
        country=country,
        material_type=material_type,
        avg_sqft=avg_sqft,
        material_list=", ".join(str(m) for m in material_list),
    )
    resp = _groq_client.chat.completions.create(
        model=_GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_completion_tokens=600,
    )
    description = resp.choices[0].message.content

    # ── Images ───────────────────────────────────────────────────────────────
    features = _STYLE_MODIFIERS.get(style, style.lower())
    seed     = random.randint(1, 9999)

    exterior_prompt = (
        f"{style} {bedrooms} bedroom house exterior in {country}, Africa, "
        f"{features}, West African architecture, tropical vegetation, "
        f"red earth ground, photorealistic, daytime, 8k, seed{seed}"
    )
    interior_prompt = (
        f"{style} {bedrooms} bedroom house interior living room in {country}, Africa, "
        f"{features}, African decor touches, wooden furniture, "
        f"bright natural lighting, photorealistic, 8k, seed{seed}"
    )

    logger.info("generate_house: %s %dBR in %s — fetching images", style, bedrooms, country)
    exterior_b64 = _generate_image(exterior_prompt)
    interior_b64 = _generate_image(interior_prompt)

    return {
        "house_name":         f"{style} {bedrooms}BR House in {country}",
        "style":              style,
        "bedrooms":           bedrooms,
        "country":            country,
        "sqft":               avg_sqft,
        "material_type":      material_type,
        "description":        description,
        "construction_cost":  construction_cost,
        "labour_cost":        labour_cost,
        "operational_cost":   op_cost,
        "grand_total":        grand_total,
        "exterior":           f"data:image/jpeg;base64,{exterior_b64}" if exterior_b64 else "",
        "interior":           f"data:image/jpeg;base64,{interior_b64}" if interior_b64 else "",
    }
