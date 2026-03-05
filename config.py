# API endpoints

TEXTSEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# Limits / delays
MAX_CITIES = 10
DETAILS_DELAY_SECONDS = 0.25          # pausa entre details requests
NEXT_PAGE_INITIAL_WAIT = 3            # espera antes de usar next_page_token
NEXT_PAGE_MAX_WAIT = 15               # max tiempo esperando token activo

# HTTP / retries
DEFAULT_TIMEOUT = 30
TEXTSEARCH_RETRIES = 8
DETAILS_RETRIES = 6
BACKOFF_BASE = 2

# Logging
LOG_FILE = "scraper.log"
LOG_LEVEL = "INFO"