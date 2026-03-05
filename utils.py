 #Funciones auxiliares 

import re
import logging
from config import LOG_FILE, LOG_LEVEL

def slugify(s: str) -> str:
    """Convierte texto a formato seguro para nombres de archivos."""
    s = s.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "", s)
    return s

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