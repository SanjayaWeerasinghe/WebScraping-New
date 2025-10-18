"""Configuration for the fashion site scraper."""

SITES = {
    "fashionbug": {
        "url": "https://fashionbug.lk/",
        "name": "Fashion Bug",
        "type": "shopify"
    },
    "thilakawardhana": {
        "url": "https://thilakawardhana.com/",
        "name": "Thilaka Wardhana",
        "type": "custom"
    },
    "nolimit": {
        "url": "https://www.nolimit.lk/",
        "name": "No Limit",
        "type": "custom"
    },
    "coolplanet": {
        "url": "https://coolplanet.lk/",
        "name": "Cool Planet",
        "type": "custom"
    }
}

# Main categories to scrape
MAIN_CATEGORIES = ["Women", "Men", "Kids"]

# Clothing types to look for
CLOTHING_TYPES = [
    "Shirts",
    "T-Shirts",
    "Blouses",
    "Tops",
    "Trousers",
    "Pants",
    "Jeans",
    "Frocks",
    "Dresses",
    "Sarees",
    "Skirts",
    "Shorts",
    "Leggings",
    "Jackets",
    "Coats",
    "Sweaters",
    "Hoodies"
]

# Scraping settings
HEADLESS = True
TIMEOUT = 60000  # 60 seconds
WAIT_FOR_LOAD = 3000  # 3 seconds
MAX_PRODUCTS_PER_CATEGORY = 30  # Limit per category

# Output settings
OUTPUT_DIR = "output"
OUTPUT_FORMAT = "json"  # json or csv
