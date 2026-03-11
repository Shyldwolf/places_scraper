"""
Carga estados y ciudades de USA desde la API de countriesnow.space (gratis, sin key).
Fallback: usa config.CITIES si la API falla.
"""
from __future__ import annotations

import requests
from functools import lru_cache

from config import CITIES  # fallback

COUNTRIESNOW_URL = "https://countriesnow.space/api/v0.1/countries/state/cities"

US_STATES: dict[str, str] = {
    "AL": "Alabama",        "AK": "Alaska",          "AZ": "Arizona",
    "AR": "Arkansas",       "CA": "California",      "CO": "Colorado",
    "CT": "Connecticut",    "DE": "Delaware",         "FL": "Florida",
    "GA": "Georgia",        "HI": "Hawaii",           "ID": "Idaho",
    "IL": "Illinois",       "IN": "Indiana",          "IA": "Iowa",
    "KS": "Kansas",         "KY": "Kentucky",         "LA": "Louisiana",
    "ME": "Maine",          "MD": "Maryland",         "MA": "Massachusetts",
    "MI": "Michigan",       "MN": "Minnesota",        "MS": "Mississippi",
    "MO": "Missouri",       "MT": "Montana",          "NE": "Nebraska",
    "NV": "Nevada",         "NH": "New Hampshire",    "NJ": "New Jersey",
    "NM": "New Mexico",     "NY": "New York",         "NC": "North Carolina",
    "ND": "North Dakota",   "OH": "Ohio",             "OK": "Oklahoma",
    "OR": "Oregon",         "PA": "Pennsylvania",     "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota",     "TN": "Tennessee",
    "TX": "Texas",          "UT": "Utah",             "VT": "Vermont",
    "VA": "Virginia",       "WA": "Washington",       "WV": "West Virginia",
    "WI": "Wisconsin",      "WY": "Wyoming",          "DC": "District of Columbia",
}


@lru_cache(maxsize=60)
def fetch_cities(state_abbr: str) -> list[str]:
    """
    Retorna lista de ciudades para un estado de USA.
    - Primer intento: countriesnow.space API
    - Fallback: config.CITIES (hardcoded)
    """
    state_name = US_STATES.get(state_abbr.upper())
    if not state_name:
        return []

    try:
        r = requests.post(
            COUNTRIESNOW_URL,
            json={"country": "United States", "state": state_name},
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("error") and data.get("data"):
            return sorted(data["data"])
    except Exception:
        pass

    return CITIES.get(state_abbr.upper(), [])
