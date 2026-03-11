# Funciones auxiliares

import re
import logging
from config import LOG_FILE, LOG_LEVEL

def slugify(s: str) -> str:
    """Convierte texto a formato seguro para nombres de archivos."""
    s = s.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "", s)
    return s

def score_lead(row: dict) -> str:
    """
    Clasifica un lead segun su potencial:
    - Hot: sin website Y pocas reviews  -> necesita todo
    - Warm: sin website O pocas reviews -> necesita algo
    - Cold: establecido, dificil de vender
    """
    has_website = bool(str(row.get("Website", "")).strip())
    try:
        reviews = int(row.get("Reviews", 0) or 0)
    except (ValueError, TypeError):
        reviews = 0
    try:
        rating = float(row.get("Rating", 5.0) or 5.0)
    except (ValueError, TypeError):
        rating = 5.0

    if not has_website and reviews < 15:
        return "Hot"
    elif not has_website or reviews < 25 or rating < 4.0:
        return "Warm"
    else:
        return "Cold"


def recommend_pitch(row: dict) -> str:
    """
    Genera una recomendacion de servicio basada en los datos del perfil.
    Mapeado a los servicios reales de YSBS.
    """
    has_website = bool(str(row.get("Website", "")).strip())
    try:
        reviews = int(row.get("Reviews", 0) or 0)
    except (ValueError, TypeError):
        reviews = 0
    try:
        rating = float(row.get("Rating", 5.0) or 5.0)
    except (ValueError, TypeError):
        rating = 5.0

    services = []

    if not has_website:
        services.append("One-Page Website")

    if reviews < 15:
        services.append("GBP Optimization + Review System")
    elif reviews < 30:
        services.append("GBP Optimization")

    if rating < 4.0:
        services.append("Reputation Repair")

    if not services:
        return "GBP Maintenance"

    return " + ".join(services)


def setup_logger() -> logging.Logger:
    """
    Configura logging a consola + archivo.
    Se llama una sola vez desde main.
    """
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
    )
    return logging.getLogger("places_scraper")