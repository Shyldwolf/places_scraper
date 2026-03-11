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

# Keywords predefinidos por nicho
KEYWORDS = [
    "Roofing",
    "HVAC",
    "Landscaping",
    "Concrete",
    "Drywall",
    "Painting",
    "Plumbing",
    "Electrical",
    "Handyman",
    "Cleaning Services",
    "Moving",
    "Auto Repair",
    "Pest Control",
    "Tree Service",
    "Pressure Washing",
    "Flooring",
    "Fence Installation",
    "Pool Service",
    "Garage Door",
    "Remodeling",
]

# Ciudades por estado
CITIES = {
    "NC": [
        "Charlotte", "Raleigh", "Durham", "Greensboro", "Winston-Salem",
        "Fayetteville", "Cary", "Wilmington", "High Point", "Concord",
        "Gastonia", "Huntersville", "Chapel Hill", "Asheville", "Kannapolis",
        "Greenville", "Burlington", "Wilson", "Mooresville", "Rocky Mount",
        "Monroe", "Goldsboro", "Hickory", "Salisbury", "Matthews",
        "Apex", "New Bern", "Indian Trail", "Sanford", "Thomasville",
    ],
    "SC": [
        "Columbia", "Charleston", "Greenville", "Spartanburg", "Rock Hill",
        "Summerville", "Goose Creek", "Hilton Head Island", "Florence",
        "Myrtle Beach", "Fort Mill", "Aiken", "Anderson", "Boiling Springs",
    ],
    "GA": [
        "Atlanta", "Augusta", "Columbus", "Savannah", "Athens",
        "Sandy Springs", "Roswell", "Macon", "Alpharetta", "Marietta",
        "Smyrna", "Valdosta", "Gainesville", "Peachtree City",
    ],
    "FL": [
        "Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg",
        "Hialeah", "Tallahassee", "Fort Lauderdale", "Port St. Lucie",
        "Cape Coral", "Pembroke Pines", "Hollywood", "Gainesville", "Miramar",
    ],
    "TX": [
        "Houston", "San Antonio", "Dallas", "Austin", "Fort Worth",
        "El Paso", "Arlington", "Corpus Christi", "Plano", "Laredo",
        "Lubbock", "Garland", "Irving", "Amarillo", "Grand Prairie",
    ],
}