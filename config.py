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

# Ciudades cercanas por area metro {estado: {ciudad: [cercanas]}}
METRO_AREAS = {
    "NC": {
        "Charlotte":     ["Concord", "Gastonia", "Huntersville", "Mooresville", "Matthews", "Monroe", "Kannapolis", "Indian Trail", "Statesville"],
        "Concord":       ["Charlotte", "Kannapolis", "Huntersville", "Mooresville"],
        "Gastonia":      ["Charlotte", "Belmont", "Bessemer City", "Kings Mountain"],
        "Huntersville":  ["Charlotte", "Concord", "Mooresville", "Cornelius", "Davidson"],
        "Mooresville":   ["Charlotte", "Huntersville", "Statesville", "Kannapolis"],
        "Matthews":      ["Charlotte", "Monroe", "Indian Trail"],
        "Monroe":        ["Charlotte", "Matthews", "Indian Trail", "Wingate"],
        "Raleigh":       ["Durham", "Cary", "Apex", "Morrisville", "Wake Forest", "Garner", "Clayton"],
        "Durham":        ["Raleigh", "Chapel Hill", "Cary", "Morrisville"],
        "Cary":          ["Raleigh", "Durham", "Apex", "Morrisville"],
        "Apex":          ["Raleigh", "Cary", "Holly Springs"],
        "Greensboro":    ["Winston-Salem", "High Point", "Burlington", "Thomasville"],
        "Winston-Salem": ["Greensboro", "High Point", "Kernersville"],
        "High Point":    ["Greensboro", "Winston-Salem", "Thomasville"],
        "Asheville":     ["Hendersonville", "Waynesville", "Black Mountain"],
        "Wilmington":    ["Leland", "Jacksonville", "Hampstead"],
        "Fayetteville":  ["Sanford", "Spring Lake", "Hope Mills"],
        "Hickory":       ["Statesville", "Lenoir", "Morganton"],
    },
    "SC": {
        "Columbia":    ["Lexington", "Irmo", "Cayce", "West Columbia", "Chapin"],
        "Charleston":  ["North Charleston", "Summerville", "Goose Creek", "Mount Pleasant"],
        "Greenville":  ["Spartanburg", "Anderson", "Mauldin", "Simpsonville", "Greer"],
        "Rock Hill":   ["Fort Mill", "Tega Cay", "Chester"],
        "Fort Mill":   ["Rock Hill", "Tega Cay", "Ballantyne"],
    },
    "GA": {
        "Atlanta":      ["Marietta", "Sandy Springs", "Roswell", "Alpharetta", "Decatur", "Smyrna", "Kennesaw"],
        "Marietta":     ["Atlanta", "Smyrna", "Kennesaw", "Acworth"],
        "Alpharetta":   ["Atlanta", "Roswell", "Johns Creek", "Cumming"],
        "Savannah":     ["Pooler", "Richmond Hill", "Hinesville"],
        "Augusta":      ["Grovetown", "Evans", "Martinez"],
    },
    "FL": {
        "Miami":       ["Hialeah", "Coral Gables", "Homestead", "Doral", "Kendall"],
        "Orlando":     ["Kissimmee", "Sanford", "Altamonte Springs", "Deltona", "Ocoee"],
        "Tampa":       ["St. Petersburg", "Clearwater", "Brandon", "Largo", "Riverview"],
        "Jacksonville":["Orange Park", "Fleming Island", "Middleburg"],
        "Fort Lauderdale": ["Pembroke Pines", "Hollywood", "Miramar", "Deerfield Beach"],
    },
    "TX": {
        "Houston":     ["Pasadena", "Sugar Land", "Pearland", "Katy", "The Woodlands", "Humble"],
        "Dallas":      ["Fort Worth", "Plano", "Irving", "Garland", "Arlington", "Mesquite", "Carrollton"],
        "San Antonio": ["New Braunfels", "Schertz", "Converse", "Universal City"],
        "Austin":      ["Round Rock", "Cedar Park", "Georgetown", "Pflugerville", "Kyle", "Buda"],
        "Fort Worth":  ["Arlington", "Mansfield", "Euless", "Bedford", "Haltom City"],
    },
}

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