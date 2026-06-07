"""
EcoChain Housing — House Image Generation Service
===================================================
File:    apps/build_assistant/image_service.py

Generates exterior + interior renders via Pollinations AI (free, no key).
Exactly 2 API calls per request — one per image.

Endpoint: POST /api/v1/layout/generate-images
"""

import base64
import logging
import random
import time
from urllib.parse import quote as url_quote

import requests

logger = logging.getLogger(__name__)

VALID_STYLES = ["Traditional", "Modern", "Minimalist", "Colonial"]

_STYLE_MODIFIERS = {
    "Traditional": "mud walls, thatched or zinc roof, courtyard layout, local African architecture",
    "Modern":      "concrete, large glass windows, flat roof, sleek modern finish",
    "Minimalist":  "simple geometric shape, clean lines, minimal windows, white exterior",
    "Colonial":    "white walls, veranda with pillars, pitched roof, symmetrical windows",
}

_POLLINATIONS_BASE = "https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&model=flux&seed={seed}"


def _fetch_image(prompt: str) -> str:
    """
    Fetch one image from Pollinations AI.
    Returns base64-encoded JPEG string.
    Raises RuntimeError after 3 failed attempts.
    """
    safe_prompt = url_quote(prompt)
    seed = random.randint(1, 9999)
    url  = _POLLINATIONS_BASE.format(prompt=safe_prompt, seed=seed)

    for attempt in range(1, 4):
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            return base64.b64encode(resp.content).decode("utf-8")
        except requests.exceptions.Timeout:
            logger.warning("Pollinations timeout (attempt %d/3)", attempt)
            if attempt < 3:
                time.sleep(3)
        except Exception as exc:
            logger.error("Pollinations error: %s", exc)
            break

    raise RuntimeError(
        "Image generation timed out after 3 attempts. "
        "Pollinations AI may be temporarily unavailable — please retry."
    )


def generate_house_images(style: str, country: str, bedrooms: int) -> dict:
    """
    Generate exterior and interior renders for the given house parameters.

    Parameters
    ----------
    style    : one of VALID_STYLES
    country  : e.g. "Nigeria", "Ghana"
    bedrooms : 1–10

    Returns
    -------
    {"exterior": "data:image/jpeg;base64,...", "interior": "data:image/jpeg;base64,..."}

    Raises
    ------
    RuntimeError if either image call fails after 3 attempts.
    """
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

    logger.info("Generating exterior image: %s %dBR in %s", style, bedrooms, country)
    exterior_b64 = _fetch_image(exterior_prompt)

    logger.info("Generating interior image: %s %dBR in %s", style, bedrooms, country)
    interior_b64 = _fetch_image(interior_prompt)

    return {
        "exterior": f"data:image/jpeg;base64,{exterior_b64}",
        "interior": f"data:image/jpeg;base64,{interior_b64}",
    }
