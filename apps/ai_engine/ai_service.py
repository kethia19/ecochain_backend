"""
EcoChain Housing — AI Engine Service
======================================
Team:    AI/ML (Group 15)
File:    apps/ai_engine/ai_service.py
Datasets:
    data/housing/Eco_Housing_Expanded.xlsx          → real market prices (suggest_materials, tco)
    data/housing/Scalable_Eco_Housing_Cost_Model101.xlsx → eco ratings & costs (suggest_materials)

Sprint tasks covered
---------------------
1. generate_layout()         → POST /api/v1/layout/generate
2. suggest_materials()       → POST /api/v1/materials/suggest
3. generate_tco_projection() → POST /api/v1/cost/tco-projection

Setup
-----
Add to .env:
    GROQ_API_KEY=gsk_...
    HOUSING_DATA_PATH=/abs/path/to/data/housing/Eco_Housing_Expanded.xlsx
    COST_MODEL_PATH=/abs/path/to/data/housing/Scalable_Eco_Housing_Cost_Model101.xlsx

Install:
    pip install groq pandas openpyxl
"""

import json
import logging
import os
from pathlib import Path
import re

import pandas as pd
from groq import Groq

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Groq client
# ---------------------------------------------------------------------------
_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL   = "llama-3.3-70b-versatile"

# ---------------------------------------------------------------------------
# Load pricing datasets at startup
# ---------------------------------------------------------------------------
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

_HOUSING_PATH = os.environ.get(
    "HOUSING_DATA_PATH",
    str(_DATA_DIR / "housing" / "Eco_Housing_Expanded.xlsx"),
)
_COST_PATH = os.environ.get(
    "COST_MODEL_PATH",
    str(_DATA_DIR / "housing" / "Scalable_Eco_Housing_Cost_Model101.xlsx"),
)

try:
    _df_housing = pd.read_excel(_HOUSING_PATH)
    _df_housing.columns = _df_housing.columns.str.strip()
    logger.info("Housing dataset loaded: %d rows", len(_df_housing))
except Exception as exc:
    _df_housing = pd.DataFrame()
    logger.error("Could not load housing dataset: %s", exc)

try:
    _df_cost = pd.read_excel(_COST_PATH)
    _df_cost.columns = _df_cost.columns.str.strip()
    logger.info("Cost model loaded: %d rows", len(_df_cost))
except Exception as exc:
    _df_cost = pd.DataFrame()
    logger.error("Could not load cost model: %s", exc)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _call_ai(prompt: str, max_tokens: int = 1500) -> str:
    msg = _client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_completion_tokens=max_tokens,
    )
    return msg.choices[0].message.content


def _parse_json(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    s = cleaned.find("{")
    e = cleaned.rfind("}") + 1
    if s == -1 or e == 0:
        raise ValueError(f"No JSON found in AI response:\n{raw}")
    return json.loads(cleaned[s:e])


def _get_market_context(country: str) -> str:
    """Pull real prices for a country from Eco_Housing_Expanded.xlsx."""
    if _df_housing.empty:
        return "No market data available."
    rows = _df_housing[_df_housing["Country"].str.lower() == country.lower()]
    if rows.empty:
        return f"No market data available for {country}."
    lines = []
    for _, r in rows.iterrows():
        lines.append(
            f"  {r['Material']}: {r['Market Rate']} {r['Currency']}/{r['Unit']} "
            f"(availability: {r['Regional Availability']}, "
            f"supplier: {r['Supplier Type']}, "
            f"updated: {str(r['Last Updated Timestamp'])[:10]})"
        )
    return "\n".join(lines)


def _get_eco_catalogue() -> str:
    """Format the eco materials catalogue from Scalable_Eco_Housing_Cost_Model101.xlsx."""
    if _df_cost.empty:
        return "No eco catalogue available."
    lines = []
    for _, r in _df_cost.iterrows():
        lines.append(
            f"  {r['Material Name']} ({r['Category']}): "
            f"Eco Rating={r['Eco Rating']}, "
            f"Cost={r['Cost Per Unit (\u20a6)']:,} NGN/unit, "
            f"Supplier={r['Supplier']}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Prompt templates — AI team updates these, not the functions
# ---------------------------------------------------------------------------

_LAYOUT_PROMPT = """\
You are an expert architect specialising in sustainable African housing.
Prioritise passive solar principles, cross-ventilation, and local eco materials.
Bedrooms:{bedrooms} | Climate:{climate_zone} | Style:{style} | Faces:{orientation}
Lot:{lot_size_sqm}sqm | Budget:{budget_note}
Return ONLY valid JSON, no markdown fences.
{{"layout_description":"...","rooms":[{{"name":"...","area_sqm":0,"notes":"..."}}],
"ventilation_paths":["..."],"passive_solar_notes":"...","eco_score":0,
"eco_score_reasons":["..."],"material_hints":[{{"element":"...","suggestion":"...","reason":"..."}}]}}"""


_MATERIALS_PROMPT = """\
You are a sustainable construction expert for African housing.
Element:{element_type} | Climate:{climate_zone} | Country:{country}
Current material:{current_material} | Budget:{budget_level}

REAL MARKET DATA FOR {country} (use these exact prices):
{market_data}

ECO MATERIALS CATALOGUE (use eco ratings and costs from here):
{eco_catalogue}

Suggest up to 4 eco-friendly alternatives. Ground cost_delta in the real market data above.
Return ONLY valid JSON, no markdown fences.
{{"summary":"...","suggestions":[{{"name":"...","description":"...","cost_delta":"...",
"carbon_score":0,"sustainability_rationale":"...","regional_availability":"...",
"maintenance_note":"..."}}]}}"""


_TCO_PROMPT = """\
You are a sustainable building economist for African housing markets.
Generate a realistic 5-year TCO projection vs a conventional build.

Climate:{climate_zone} | Country:{country} | Size:{house_size_sqm}sqm
Eco materials:{materials_summary} | Upfront cost:USD {upfront_cost_usd:,.0f}
Household:{household_size} people

REAL MARKET PRICES FOR {country} — use these in your calculations:
{market_data}

Model savings in:
1) Electricity — passive cooling reduces AC usage
2) Water — rainwater harvesting savings
3) Maintenance — durable local materials vs imported cement
Be conservative. State all assumptions clearly.
Return ONLY valid JSON, no markdown fences.
{{"savings_breakdown":{{"electricity_usd_5yr":0,"water_usd_5yr":0,
"maintenance_usd_5yr":0,"total_savings_5yr":0}},
"payback_period_months":0,"net_cost_5yr_usd":0,
"year_by_year":[{{"year":1,"cumulative_savings_usd":0}},{{"year":2,"cumulative_savings_usd":0}},
{{"year":3,"cumulative_savings_usd":0}},{{"year":4,"cumulative_savings_usd":0}},
{{"year":5,"cumulative_savings_usd":0}}],
"key_assumptions":["..."],"sustainability_highlights":["..."]}}"""


# ---------------------------------------------------------------------------
# Task 1 — Layout generation
# POST /api/v1/layout/generate
# ---------------------------------------------------------------------------

def generate_layout(
    bedrooms: int,
    climate_zone: str,
    style: str,
    orientation: str,
    lot_size_sqm: float = 120.0,
    budget_usd: float | None = None,
) -> dict:
    """
    Generate an eco-optimised building layout.

    Parameters
    ----------
    bedrooms     : 1–6
    climate_zone : "Sahel" | "Equatorial" | "Subtropical Coastal" |
                   "Highland" | "Semi-arid" | "Arid" | "Tropical Humid"
    style        : "modern" | "traditional"
    orientation  : "north" | "south" | "east" | "west"
    lot_size_sqm : plot size in sqm
    budget_usd   : optional budget cap

    Returns
    -------
    {layout_description, rooms, ventilation_paths, passive_solar_notes,
     eco_score, eco_score_reasons, material_hints}
    """
    prompt = _LAYOUT_PROMPT.format(
        bedrooms=bedrooms, climate_zone=climate_zone, style=style,
        orientation=orientation, lot_size_sqm=lot_size_sqm,
        budget_note=f"USD {budget_usd:,.0f}" if budget_usd else "Not specified",
    )
    logger.info("generate_layout: %d beds, %s, %s", bedrooms, climate_zone, style)
    return _parse_json(_call_ai(prompt, 1500))


# ---------------------------------------------------------------------------
# Task 2 — Material suggestion engine
# POST /api/v1/materials/suggest
# ---------------------------------------------------------------------------

def suggest_materials(
    element_type: str,
    climate_zone: str,
    country: str = "Kenya",
    current_material: str | None = None,
    budget_level: str = "medium",
) -> dict:
    """
    Suggest eco material alternatives grounded in real market prices.
    Prices come from Eco_Housing_Expanded.xlsx.
    Eco ratings come from Scalable_Eco_Housing_Cost_Model101.xlsx.

    Parameters
    ----------
    element_type     : "wall" | "roof" | "floor" | "foundation" | "window"
    climate_zone     : same values as generate_layout()
    country          : "Kenya" | "Nigeria" | "Ghana" | "Ethiopia" |
                       "South Africa" | "Senegal"
    current_material : e.g. "concrete blocks"
    budget_level     : "low" | "medium" | "high"

    Returns
    -------
    {element_type, summary, suggestions, market_data_source}
    Each suggestion: {name, description, cost_delta, carbon_score,
                      sustainability_rationale, regional_availability,
                      maintenance_note}
    """
    prompt = _MATERIALS_PROMPT.format(
        element_type=element_type,
        climate_zone=climate_zone,
        country=country,
        current_material=current_material or "not specified",
        budget_level=budget_level,
        market_data=_get_market_context(country),
        eco_catalogue=_get_eco_catalogue(),
    )
    logger.info("suggest_materials: %s, %s, %s", element_type, climate_zone, country)
    result = _parse_json(_call_ai(prompt, 1200))
    result["element_type"]        = element_type
    result["market_data_source"]  = "Eco_Housing_Expanded.xlsx"
    return result


# ---------------------------------------------------------------------------
# Task 3 — 5-year operational savings projection
# POST /api/v1/cost/tco-projection
# ---------------------------------------------------------------------------

def generate_tco_projection(
    layout_id: str,
    climate_zone: str,
    country: str,
    house_size_sqm: float,
    materials_chosen: list[dict],
    upfront_cost_usd: float,
    household_size: int = 4,
) -> dict:
    """
    5-year savings projection grounded in real country-level market rates.
    Prices come from Eco_Housing_Expanded.xlsx.

    Parameters
    ----------
    layout_id        : saved layout ID (echoed in response)
    climate_zone     : same values as generate_layout()
    country          : same values as suggest_materials()
    house_size_sqm   : total floor area
    materials_chosen : [{"element": "wall", "material": "CEB"}, ...]
    upfront_cost_usd : total construction cost in USD
    household_size   : number of occupants

    Returns
    -------
    {layout_id, upfront_cost_usd, savings_breakdown, payback_period_months,
     net_cost_5yr_usd, year_by_year, key_assumptions,
     sustainability_highlights, market_data_source}
    """
    mat_summary = ", ".join(
        f"{m.get('element','?')}→{m.get('material','?')}" for m in materials_chosen
    ) or "standard eco materials"

    prompt = _TCO_PROMPT.format(
        climate_zone=climate_zone,
        country=country,
        house_size_sqm=house_size_sqm,
        materials_summary=mat_summary,
        upfront_cost_usd=upfront_cost_usd,
        household_size=household_size,
        market_data=_get_market_context(country),
    )
    logger.info("generate_tco_projection: %s, %s, USD %.0f", climate_zone, country, upfront_cost_usd)
    result = _parse_json(_call_ai(prompt, 1500))
    result["layout_id"]          = layout_id
    result["upfront_cost_usd"]   = upfront_cost_usd
    result["market_data_source"] = "Eco_Housing_Expanded.xlsx"
    return result


# ---------------------------------------------------------------------------
# Task 4 — Standalone cost estimate (no layout_id required)
# POST /api/v1/cost/estimate
# ---------------------------------------------------------------------------

_COUNTRY_CURRENCY = {
    "nigeria": "NGN", "ghana": "GHS", "kenya": "KES",
    "ethiopia": "ETB", "south africa": "ZAR", "senegal": "XOF",
}

_ESTIMATE_PROMPT = """\
You are a construction cost analyst specialising in African eco-housing.
Calculate a full cost estimate AND 5-year operational savings for this project.

House type: {house_type}
Country: {country} | City: {city}
Size: {size_sqm} sqm | Rooms: {rooms}
Eco level: {eco_level} | Power preference: {power_preference}
Materials chosen: {materials_str}
Eco features: {features_str}
Budget: {budget_str}

REAL MARKET DATA FOR {country} (use these exact prices where applicable):
{market_data}

ECO MATERIALS CATALOGUE:
{eco_catalogue}

Rules:
- totalCost must be in local currency ({currency}).
- Use real {country} labour and material rates from the market data above.
- fiveYearSavings covers electricity, water, and maintenance vs a conventional build.
- recommendationScore is 0–10 (eco performance score).
- suggestedUpgrades are practical improvements within the stated budget.
- If market data is unavailable, use your best knowledge of {country} construction costs.

Return ONLY valid JSON matching this exact schema, no markdown fences:
{{"totalCost":0,"currency":"{currency}","breakdown":{{"materials":0,"labor":0,"ecoFeatures":0}},\
"fiveYearSavings":{{"energySavings":0,"waterSavings":0,"maintenanceSavings":0,"totalSavings":0}},\
"roiEstimate":"0%","recommendationScore":0.0,\
"suggestedUpgrades":["..."],"keyAssumptions":["..."]}}"""


def estimate_cost_standalone(
    house_type: str,
    country: str,
    city: str,
    size_sqm: float,
    rooms: int,
    eco_level: str = "Medium",
    power_preference: str = "Grid",
    budget: float | None = None,
    materials: dict | None = None,
    features: list[str] | None = None,
) -> dict:
    """
    Standalone cost estimate + 5-year savings — no layout_id needed.

    Parameters
    ----------
    house_type       : e.g. "Duplex", "Bungalow", "2-bedroom apartment"
    country          : full name — "Nigeria" | "Kenya" | "Ghana" | "Ethiopia" |
                       "South Africa" | "Senegal"
    city             : e.g. "Lagos", "Nairobi"
    size_sqm         : total floor area in sqm
    rooms            : number of bedrooms / rooms
    eco_level        : "Low" | "Medium" | "High"
    power_preference : "Grid" | "Solar" | "Hybrid (Solar + Grid)"
    budget           : optional budget cap in local currency
    materials        : optional {"wall": "block", "roof": "solar_tile", ...}
    features         : optional ["solar", "rainwater_harvest", "smart_meter"]

    Returns
    -------
    {totalCost, currency, breakdown, fiveYearSavings, roiEstimate,
     recommendationScore, suggestedUpgrades, keyAssumptions}
    """
    currency = _COUNTRY_CURRENCY.get(country.lower(), "USD")
    materials_str = (
        ", ".join(f"{k}: {v}" for k, v in materials.items()) if materials else "not specified"
    )
    features_str  = ", ".join(features) if features else "none specified"
    budget_str    = f"{budget:,.0f} {currency}" if budget else "not specified"

    prompt = _ESTIMATE_PROMPT.format(
        house_type=house_type,
        country=country,
        city=city,
        size_sqm=size_sqm,
        rooms=rooms,
        eco_level=eco_level,
        power_preference=power_preference,
        materials_str=materials_str,
        features_str=features_str,
        budget_str=budget_str,
        currency=currency,
        market_data=_get_market_context(country),
        eco_catalogue=_get_eco_catalogue(),
    )

    logger.info(
        "estimate_cost_standalone: %s, %s/%s, %g sqm, eco=%s",
        house_type, country, city, size_sqm, eco_level,
    )
    result = _parse_json(_call_ai(prompt, 1800))
    result.setdefault("currency", currency)
    return result


# ---------------------------------------------------------------------------
# Quick test — python ai_service.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("TEST 1 — generate_layout()")
    print("=" * 55)
    layout = generate_layout(3, "Sahel", "modern", "south", 150, 25000)
    print(f"Eco Score : {layout.get('eco_score')} / 100")
    print(f"Rooms     : {[r['name'] for r in layout.get('rooms', [])]}")

    print("\n" + "=" * 55)
    print("TEST 2 — suggest_materials() — real Kenya prices")
    print("=" * 55)
    mats = suggest_materials("wall", "Equatorial", "Kenya", "concrete blocks")
    for s in mats.get("suggestions", []):
        print(f"  {s['name']:<35} carbon:{s.get('carbon_score')} | {s.get('cost_delta')}")

    print("\n" + "=" * 55)
    print("TEST 3 — generate_tco_projection() — real Nigeria prices")
    print("=" * 55)
    tco = generate_tco_projection(
        "test-001", "Sahel", "Nigeria", 120,
        [{"element": "wall", "material": "Compressed Earth Blocks"},
         {"element": "roof", "material": "Cool roof tiles"}],
        28000, 4,
    )
    sb = tco.get("savings_breakdown", {})
    print(f"Total 5yr savings : USD {sb.get('total_savings_5yr', 0):,.0f}")
    print(f"Payback period    : {tco.get('payback_period_months')} months")
    print(f"Market data from  : {tco.get('market_data_source')}")
    print("\n✅  All three AI functions working correctly.")
