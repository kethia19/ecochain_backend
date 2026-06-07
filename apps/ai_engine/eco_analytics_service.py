"""
EcoChain Housing — Eco Analytics Service
==========================================
Team:    AI/ML (Group 15)
File:    apps/ai_engine/eco_analytics_service.py

Covers the two analytics modules that live in ai_engine:
  • Maintenance insights   → GET  /api/v1/maintenance/insights
  • Education content recs → GET  /api/v1/education/recommendations

EcoScore logic lives in apps/ecoscore/service.py.
"""

import logging
import os
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


# ──────────────────────────────────────────────────────────────────────────────
# Maintenance dataset
# ──────────────────────────────────────────────────────────────────────────────

_MAINT_FILE = os.environ.get(
    "MAINTENANCE_DATA_PATH",
    str(_DATA_DIR / "maintenance" / "Eco-Chain_Housing_Maintenance_Dataset.xlsx"),
)

try:
    _maint_xls       = pd.ExcelFile(_MAINT_FILE)
    _MAINT_ANALYTICS = pd.read_excel(_maint_xls, "Maintenance_Analytics")
    logger.info("Maintenance dataset loaded (%d rows)", len(_MAINT_ANALYTICS))
except Exception as exc:
    _MAINT_ANALYTICS = pd.DataFrame()
    logger.error("Could not load Maintenance dataset: %s", exc)


# ──────────────────────────────────────────────────────────────────────────────
# Education Hub dataset
# ──────────────────────────────────────────────────────────────────────────────

_EDU_FILE = os.environ.get(
    "EDUCATION_DATA_PATH",
    str(_DATA_DIR / "education" / "eco_housing_education_hub.xlsx"),
)

try:
    _edu_xls         = pd.ExcelFile(_EDU_FILE)
    _CONTENT_LIBRARY = pd.read_excel(_edu_xls, "Content Library ")
    _CONTENT_CATS    = pd.read_excel(_edu_xls, "Education Category ")
    _USER_ACTIVITY   = pd.read_excel(_edu_xls, " User Learning Activity ")
    logger.info("Education dataset loaded (%d content items)", len(_CONTENT_LIBRARY))
except Exception as exc:
    _CONTENT_LIBRARY = _CONTENT_CATS = _USER_ACTIVITY = pd.DataFrame()
    logger.error("Could not load Education dataset: %s", exc)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _col(df: pd.DataFrame, *keywords: str) -> str | None:
    """Return first column name whose lowercase form contains any keyword."""
    for kw in keywords:
        match = next((c for c in df.columns if kw in c.lower()), None)
        if match:
            return match
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def get_maintenance_insights() -> dict:
    """
    Return analytics from the Maintenance_Analytics sheet.

    Returns
    -------
    {total_tasks, completed_tasks, completion_rate, priority_breakdown,
     avg_compliance_by_category, urgent_items, recommendation}
    """
    if _MAINT_ANALYTICS.empty:
        raise RuntimeError("Maintenance dataset not loaded. Check MAINTENANCE_DATA_PATH.")

    df = _MAINT_ANALYTICS.copy()

    c_task     = _col(df, "task")
    c_category = _col(df, "category")
    c_status   = _col(df, "compliance_status")
    c_score    = _col(df, "compliance_score")
    c_late     = _col(df, "days_late")

    missing = [n for n, v in [("task", c_task), ("category", c_category),
                               ("compliance_status", c_status),
                               ("compliance_score", c_score), ("days_late", c_late)] if not v]
    if missing:
        raise ValueError(f"Expected columns not found in Maintenance_Analytics: {missing}")

    def _priority(status_val, days_late):
        s  = str(status_val).lower()
        dl = days_late if pd.notna(days_late) else 0
        if "overdue" in s or dl > 7:  return "Critical"
        if "late"    in s and dl > 2: return "High"
        if "late"    in s:            return "Medium"
        return "Low"

    df["Priority"]    = df.apply(lambda r: _priority(r[c_status], r[c_late]), axis=1)
    priority_counts   = df.groupby("Priority").size().to_dict()
    score_by_category = df.groupby(c_category)[c_score].mean().round(1).to_dict()
    urgent            = df[df["Priority"].isin(["Critical", "High"])].head(5)

    total_tasks     = len(df)
    completed_tasks = len(df[df[c_status].str.lower() == "on-time"])
    completion_rate = round((completed_tasks / total_tasks) * 100, 1) if total_tasks else 0.0

    critical = priority_counts.get("Critical", 0)
    rec = (f"You have {critical} critical task(s). Address those first!"
           if critical else "All maintenance on track ✓")

    return {
        "total_tasks":               total_tasks,
        "completed_tasks":           completed_tasks,
        "completion_rate":           f"{completion_rate}%",
        "priority_breakdown":        priority_counts,
        "avg_compliance_by_category": score_by_category,
        "urgent_items":              urgent[[c_task, c_category, "Priority", c_status, c_late]].to_dict("records"),
        "recommendation":            rec,
    }


def _clean_df(df):
    """Strip trailing/leading whitespace from column names and all string values."""
    df = df.copy()
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df


def recommend_content(user_id: str, top_n: int = 5) -> list:
    """
    Return personalised content recommendations for a user.

    Parameters
    ----------
    user_id : str   — authenticated user identifier
    top_n   : int   — max results (default 5, max 20)

    Returns
    -------
    list of content dicts
    """
    if _CONTENT_LIBRARY.empty:
        raise RuntimeError("Education dataset not loaded. Check EDUCATION_DATA_PATH.")

    # Strip all column names and string cell values (Excel files often have trailing spaces)
    content_df = _clean_df(_CONTENT_LIBRARY)
    user_df    = _clean_df(_USER_ACTIVITY)

    # Detect columns by exact or partial lowercased match after cleaning
    def _find_col(df, *candidates):
        lower_map = {c.lower(): c for c in df.columns}
        for c in candidates:
            if c.lower() in lower_map:
                return lower_map[c.lower()]
        # fallback: substring match
        for c in candidates:
            match = next((orig for orig in df.columns if c.lower() in orig.lower()), None)
            if match:
                return match
        return None

    content_id_col = _find_col(content_df, "content_id", "id")
    title_col      = _find_col(content_df, "title")
    cat_col        = _find_col(content_df, "category")  # holds the category name directly
    diff_col       = _find_col(content_df, "difficulty_level", "difficulty")

    user_id_col  = _find_col(user_df, "user_id")
    user_cid_col = _find_col(user_df, "content_id")

    # Items already seen/completed by this user
    completed = []
    if user_id_col and user_cid_col and not user_df.empty:
        completed = user_df[user_df[user_id_col] == user_id][user_cid_col].tolist()

    available = (
        content_df[~content_df[content_id_col].isin(completed)].copy()
        if content_id_col and completed
        else content_df.copy()
    )

    if available.empty:
        return [{"message": "You've completed all available content!"}]

    # Beginner-first scoring — case-insensitive (values may come from Excel mixed case)
    available = available.copy()
    available["_rank"] = 3.0
    if diff_col:
        diff_map = {"beginner": 1, "intermediate": 0, "advanced": -0.5}
        available["_rank"] += (
            available[diff_col].str.lower().map(diff_map).fillna(0)
        )

    cols = [c for c in [content_id_col, title_col, cat_col, diff_col] if c]
    return (
        available[cols + ["_rank"]]
        .sort_values("_rank", ascending=False)
        .head(top_n)
        .drop(columns=["_rank"])
        .to_dict("records")
    )
