"""
FastAPI backend for Fashion Scraper Dashboard.
Serves data from SQLite database to the React frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
from pathlib import Path
from datetime import datetime


app = FastAPI(title="Fashion Scraper API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Alternative
        "http://localhost:8080",  # Current frontend port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).parent / "fashion_scraper.db"


# Pydantic models for API responses
class ScrapedItem(BaseModel):
    id: str
    competitor: str  # "fashionbug" | "coolplanet"
    clothingType: str  # "men" | "women"
    clothingSubtype: str  # clothing_type from database
    name: str
    price: float
    colors: List[str]  # All colors from the product
    imageUrl: Optional[str]  # Product image URL
    dateScraped: str


class PaginatedResponse(BaseModel):
    items: List[ScrapedItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class FilterOptions(BaseModel):
    competitors: List[str]
    clothing_types: List[str]
    clothing_subtypes: List[str]


class PriceHistoryItem(BaseModel):
    product_id: int
    product_name: str
    product_url: str
    site: str
    prices: List[dict]  # [{date, price, price_numeric}, ...]


class ColorTrendItem(BaseModel):
    color: str
    count: int
    site: str
    clothing_type: str


class StatsResponse(BaseModel):
    total_products: int
    total_sessions: int
    sites: dict
    price_range: dict


def get_db():
    """Get database connection."""
    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail="Database not found")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def map_site_name(site: str) -> str:
    """Map site name to frontend format."""
    if not site:
        return "unknown"
    site_lower = site.lower().replace(" ", "")
    if "fashion" in site_lower or "bug" in site_lower:
        return "fashionbug"
    elif "cool" in site_lower or "planet" in site_lower:
        return "coolplanet"
    return site_lower


def map_clothing_subtype(clothing_type: str) -> str:
    """Map clothing_type from database to frontend clothingSubtype."""
    if not clothing_type:
        return "tshirt"

    type_lower = clothing_type.lower()

    # Map database clothing types to frontend subtypes
    if "shirt" in type_lower and "t-" not in type_lower:
        return "shirt"
    elif "t-shirt" in type_lower or "tshirt" in type_lower:
        return "tshirt"
    elif "jean" in type_lower or "denim" in type_lower:
        return "jean"
    elif "trouser" in type_lower or "pant" in type_lower or "chino" in type_lower:
        return "trouser"
    elif "skirt" in type_lower:
        return "skirt"
    elif "saree" in type_lower or "sari" in type_lower:
        return "saree"
    elif "frock" in type_lower or "dress" in type_lower:
        return "frock"
    else:
        return "tshirt"  # Default


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "message": "Fashion Scraper API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/products", response_model=PaginatedResponse)
def get_products(
    site: Optional[str] = None,
    gender: Optional[str] = None,
    clothing_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get all products with latest price and color data (paginated).

    Query params:
    - site: Filter by site (fashionbug/coolplanet)
    - gender: Filter by gender (men/women)
    - clothing_type: Filter by clothing type
    - page: Page number (default 1)
    - page_size: Items per page (default 10)
    """
    conn = get_db()
    cursor = conn.cursor()

    # Build date filter for subqueries
    date_filter_ph = ""
    date_filter_ch = ""
    date_filter_ih = ""
    date_params = []

    if start_date and end_date:
        date_filter_ph = " AND DATE(scraped_at) BETWEEN ? AND ?"
        date_filter_ch = " AND DATE(scraped_at) BETWEEN ? AND ?"
        date_filter_ih = " AND DATE(scraped_at) BETWEEN ? AND ?"
        date_params = [start_date, end_date, start_date, end_date, start_date, end_date]
    elif start_date:
        date_filter_ph = " AND DATE(scraped_at) >= ?"
        date_filter_ch = " AND DATE(scraped_at) >= ?"
        date_filter_ih = " AND DATE(scraped_at) >= ?"
        date_params = [start_date, start_date, start_date]
    elif end_date:
        date_filter_ph = " AND DATE(scraped_at) <= ?"
        date_filter_ch = " AND DATE(scraped_at) <= ?"
        date_filter_ih = " AND DATE(scraped_at) <= ?"
        date_params = [end_date, end_date, end_date]

    # Build base query with filters - get latest records within date range
    base_query = f"""
        FROM products p
        LEFT JOIN product_names pn ON p.id = pn.product_id
        LEFT JOIN price_history ph ON p.id = ph.product_id
        LEFT JOIN color_history ch ON p.id = ch.product_id
        LEFT JOIN image_history ih ON p.id = ih.product_id
        WHERE p.is_active = 1
          AND pn.id IN (SELECT MAX(id) FROM product_names GROUP BY product_id)
          AND (ph.id IS NULL OR ph.id IN (SELECT MAX(id) FROM price_history WHERE product_id = p.id{date_filter_ph}))
          AND (ch.id IS NULL OR ch.id IN (SELECT MAX(id) FROM color_history WHERE product_id = p.id{date_filter_ch}))
          AND (ih.id IS NULL OR ih.id IN (SELECT MAX(id) FROM image_history WHERE product_id = p.id{date_filter_ih}))
    """

    params = date_params.copy()

    if site:
        if site.lower() == "fashionbug":
            base_query += " AND (LOWER(p.site) LIKE '%fashion%' OR LOWER(p.site) LIKE '%bug%')"
        elif site.lower() == "coolplanet":
            base_query += " AND (LOWER(p.site) LIKE '%cool%' OR LOWER(p.site) LIKE '%planet%')"

    if gender:
        base_query += " AND LOWER(p.gender) = ?"
        params.append(gender.lower())

    if clothing_type:
        base_query += " AND LOWER(p.clothing_type) LIKE ?"
        params.append(f"%{clothing_type.lower()}%")

    # Get total count
    count_query = f"SELECT COUNT(DISTINCT p.id) {base_query}"
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size  # Ceiling division
    offset = (page - 1) * page_size

    # Get paginated results
    data_query = f"""
        SELECT DISTINCT
            p.id,
            p.product_url,
            p.site,
            p.gender,
            p.clothing_type,
            pn.name,
            ph.price,
            ph.price_numeric,
            ph.scraped_at as price_date,
            ch.colors,
            ih.image_url
        {base_query}
        ORDER BY p.gender, p.site, p.id
        LIMIT ? OFFSET ?
    """

    cursor.execute(data_query, params + [page_size, offset])
    products = cursor.fetchall()

    # Map to frontend format
    result = []
    for product in products:
        # Parse colors
        colors_list = []
        if product['colors']:
            try:
                colors_list = json.loads(product['colors'])
            except:
                colors_list = []

        if not colors_list:
            colors_list = ["Unknown"]

        # Map gender to clothingType
        gender_lower = product['gender'].lower() if product['gender'] else ""
        clothing_type_mapped = "men" if gender_lower == "men" else "women"

        result.append(ScrapedItem(
            id=str(product['id']),
            competitor=map_site_name(product['site']),
            clothingType=clothing_type_mapped,
            clothingSubtype=product['clothing_type'] or "Unknown",
            name=product['name'] or "Unknown Product",
            price=product['price_numeric'] or 0.0,
            colors=colors_list,
            imageUrl=product['image_url'] if product['image_url'] else None,
            dateScraped=product['price_date'][:10] if product['price_date'] else datetime.now().strftime("%Y-%m-%d")
        ))

    conn.close()

    return PaginatedResponse(
        items=result,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@app.get("/api/price-history/{product_id}", response_model=PriceHistoryItem)
def get_price_history(product_id: int):
    """Get price history for a specific product."""
    conn = get_db()
    cursor = conn.cursor()

    # Get product info
    cursor.execute("""
        SELECT p.id, p.product_url, p.site, pn.name
        FROM products p
        LEFT JOIN product_names pn ON p.id = pn.product_id
        WHERE p.id = ?
          AND pn.id IN (SELECT MAX(id) FROM product_names WHERE product_id = p.id)
    """, (product_id,))

    product = cursor.fetchone()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get price history
    cursor.execute("""
        SELECT price, price_numeric, scraped_at
        FROM price_history
        WHERE product_id = ?
        ORDER BY scraped_at ASC
    """, (product_id,))

    prices = cursor.fetchall()

    price_list = [
        {
            "date": p['scraped_at'],
            "price": p['price'],
            "price_numeric": p['price_numeric']
        }
        for p in prices
    ]

    conn.close()

    return PriceHistoryItem(
        product_id=product['id'],
        product_name=product['name'] or "Unknown",
        product_url=product['product_url'],
        site=product['site'] or "Unknown",
        prices=price_list
    )


@app.get("/api/color-trends", response_model=List[ColorTrendItem])
def get_color_trends(site: Optional[str] = None):
    """Get color distribution across all products."""
    conn = get_db()
    cursor = conn.cursor()

    # Get all color data
    query = """
        SELECT p.site, p.clothing_type, ch.colors
        FROM products p
        JOIN color_history ch ON p.id = ch.product_id
        WHERE p.is_active = 1
          AND ch.id IN (SELECT MAX(id) FROM color_history GROUP BY product_id)
    """

    params = []
    if site:
        if site.lower() == "fashionbug":
            query += " AND (LOWER(p.site) LIKE '%fashion%' OR LOWER(p.site) LIKE '%bug%')"
        elif site.lower() == "coolplanet":
            query += " AND (LOWER(p.site) LIKE '%cool%' OR LOWER(p.site) LIKE '%planet%')"

    cursor.execute(query, params)
    results = cursor.fetchall()

    # Count colors
    color_counts = {}

    for row in results:
        site_name = map_site_name(row['site'])
        clothing_type = row['clothing_type'] or "unknown"

        if row['colors']:
            try:
                colors = json.loads(row['colors'])
                for color in colors:
                    key = (color, site_name, clothing_type)
                    color_counts[key] = color_counts.get(key, 0) + 1
            except:
                continue

    # Convert to response format
    result = [
        ColorTrendItem(
            color=color,
            count=count,
            site=site_name,
            clothing_type=clothing_type
        )
        for (color, site_name, clothing_type), count in color_counts.items()
    ]

    # Sort by count descending
    result.sort(key=lambda x: x.count, reverse=True)

    conn.close()
    return result


@app.get("/api/filter-options", response_model=FilterOptions)
def get_filter_options():
    """Get available filter options based on actual data."""
    conn = get_db()
    cursor = conn.cursor()

    # Get unique sites (competitors)
    cursor.execute("""
        SELECT DISTINCT site
        FROM products
        WHERE is_active = 1 AND site IS NOT NULL AND site != ''
        ORDER BY site
    """)
    sites = [map_site_name(row['site']) for row in cursor.fetchall()]
    competitors = list(set(sites))  # Remove duplicates

    # Get unique genders (clothing types - main_category)
    cursor.execute("""
        SELECT DISTINCT gender
        FROM products
        WHERE is_active = 1 AND gender IS NOT NULL AND gender != ''
        ORDER BY gender
    """)
    clothing_types = [row['gender'] for row in cursor.fetchall()]

    # Get unique clothing types (clothing subtypes)
    cursor.execute("""
        SELECT DISTINCT clothing_type
        FROM products
        WHERE is_active = 1 AND clothing_type IS NOT NULL AND clothing_type != ''
        ORDER BY clothing_type
    """)
    clothing_subtypes = [row['clothing_type'] for row in cursor.fetchall()]

    conn.close()

    return FilterOptions(
        competitors=sorted(competitors),
        clothing_types=sorted(clothing_types),
        clothing_subtypes=sorted(clothing_subtypes)
    )


@app.get("/api/price-trends")
def get_price_trends(
    site: Optional[str] = None,
    gender: Optional[str] = None,
    clothing_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get price trends over time."""
    conn = get_db()
    cursor = conn.cursor()

    # Build query with filters
    query = """
        SELECT
            DATE(ph.scraped_at) as date,
            p.site,
            p.gender,
            AVG(ph.price_numeric) as avg_price,
            MIN(ph.price_numeric) as min_price,
            MAX(ph.price_numeric) as max_price,
            COUNT(*) as product_count
        FROM price_history ph
        JOIN products p ON ph.product_id = p.id
        WHERE p.is_active = 1
    """

    params = []

    if site:
        if site.lower() == "fashionbug":
            query += " AND (LOWER(p.site) LIKE '%fashion%' OR LOWER(p.site) LIKE '%bug%')"
        elif site.lower() == "coolplanet":
            query += " AND (LOWER(p.site) LIKE '%cool%' OR LOWER(p.site) LIKE '%planet%')"

    if gender:
        query += " AND LOWER(p.gender) = ?"
        params.append(gender.lower())

    if clothing_type:
        query += " AND LOWER(p.clothing_type) LIKE ?"
        params.append(f"%{clothing_type.lower()}%")

    if start_date:
        query += " AND DATE(ph.scraped_at) >= ?"
        params.append(start_date)

    if end_date:
        query += " AND DATE(ph.scraped_at) <= ?"
        params.append(end_date)

    query += """
        GROUP BY DATE(ph.scraped_at), p.site, p.gender
        ORDER BY DATE(ph.scraped_at), p.site, p.gender
    """

    cursor.execute(query, params)
    results = cursor.fetchall()

    data = [
        {
            "date": row['date'],
            "site": map_site_name(row['site']),
            "gender": row['gender'],
            "avg_price": round(row['avg_price'], 2) if row['avg_price'] else 0,
            "min_price": round(row['min_price'], 2) if row['min_price'] else 0,
            "max_price": round(row['max_price'], 2) if row['max_price'] else 0,
            "product_count": row['product_count']
        }
        for row in results
    ]

    conn.close()
    return data


@app.get("/api/product-timeline")
def get_product_timeline(
    site: Optional[str] = None,
    gender: Optional[str] = None,
    clothing_type: Optional[str] = None
):
    """Get product count by date first seen for launch timeline."""
    conn = get_db()
    cursor = conn.cursor()

    # Build query with filters - count products by when they were first seen
    query = """
        SELECT
            DATE(p.first_seen) as date,
            p.site,
            p.gender,
            COUNT(DISTINCT p.id) as product_count
        FROM products p
        WHERE p.is_active = 1
    """

    params = []

    if site:
        if site.lower() == "fashionbug":
            query += " AND (LOWER(p.site) LIKE '%fashion%' OR LOWER(p.site) LIKE '%bug%')"
        elif site.lower() == "coolplanet":
            query += " AND (LOWER(p.site) LIKE '%cool%' OR LOWER(p.site) LIKE '%planet%')"

    if gender:
        query += " AND LOWER(p.gender) = ?"
        params.append(gender.lower())

    if clothing_type:
        query += " AND LOWER(p.clothing_type) LIKE ?"
        params.append(f"%{clothing_type.lower()}%")

    query += """
        GROUP BY DATE(p.first_seen), p.site, p.gender
        ORDER BY DATE(p.first_seen) ASC
    """

    cursor.execute(query, params)
    results = cursor.fetchall()

    # Group by date and aggregate counts
    timeline_data = {}
    for row in results:
        date = row['date']
        if date not in timeline_data:
            timeline_data[date] = {
                'date': date,
                'total': 0,
                'by_site_gender': {}
            }

        site_name = map_site_name(row['site']) if row['site'] else None
        gender_val = row['gender']

        if site_name and gender_val:
            key = f"{site_name}_{gender_val}"
            timeline_data[date]['by_site_gender'][key] = timeline_data[date]['by_site_gender'].get(key, 0) + row['product_count']
            timeline_data[date]['total'] += row['product_count']

    # Convert to list format for the chart
    data = []
    for date, info in sorted(timeline_data.items()):
        item = {
            'date': date,
            'total': info['total']
        }
        # Add individual site/gender counts as separate keys
        for key, count in info['by_site_gender'].items():
            parts = key.split('_')
            if len(parts) == 2:
                site, gender_val = parts
                # Map site names to match frontend format
                site_formatted = "FashionBug" if site == "fashionbug" else "CoolPlanet"
                gender_formatted = gender_val.capitalize()
                formatted_key = f"{site_formatted} {gender_formatted}"
                item[formatted_key] = count
        data.append(item)

    conn.close()
    return data


@app.get("/api/color-price-trends")
def get_color_price_trends(
    site: Optional[str] = None,
    gender: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get average price trends for each color category over time."""
    conn = get_db()
    cursor = conn.cursor()

    # Build query to get colors and prices over time
    query = """
        SELECT
            DATE(ph.scraped_at) as date,
            ch.colors,
            p.site,
            p.gender,
            ph.price_numeric
        FROM products p
        JOIN price_history ph ON p.id = ph.product_id
        JOIN color_history ch ON p.id = ch.product_id
        WHERE p.is_active = 1
          AND DATE(ph.scraped_at) = DATE(ch.scraped_at)
    """

    params = []

    if site:
        if site.lower() == "fashionbug":
            query += " AND (LOWER(p.site) LIKE '%fashion%' OR LOWER(p.site) LIKE '%bug%')"
        elif site.lower() == "coolplanet":
            query += " AND (LOWER(p.site) LIKE '%cool%' OR LOWER(p.site) LIKE '%planet%')"

    if gender:
        query += " AND LOWER(p.gender) = ?"
        params.append(gender.lower())

    if start_date:
        query += " AND DATE(ph.scraped_at) >= ?"
        params.append(start_date)

    if end_date:
        query += " AND DATE(ph.scraped_at) <= ?"
        params.append(end_date)

    query += " ORDER BY DATE(ph.scraped_at)"

    cursor.execute(query, params)
    results = cursor.fetchall()

    # Color categorization function (same as frontend)
    def categorize_color(color_name):
        if not color_name:
            return "Other"
        color = color_name.lower()

        # Black shades
        if any(x in color for x in ["black", "ebony", "jet", "onyx", "coal", "raisin", "licorice"]):
            return "Black"
        # White shades
        elif any(x in color for x in ["white", "ivory", "cream", "beige", "eggshell", "ghost"]):
            return "White"
        # Gray shades
        elif any(x in color for x in ["gray", "grey", "silver", "ash", "slate", "charcoal", "grullo", "taupe"]):
            return "Gray"
        # Red shades
        elif any(x in color for x in ["red", "crimson", "scarlet", "ruby", "burgundy", "maroon", "cardinal", "brick"]):
            return "Red"
        # Blue shades
        elif any(x in color for x in ["blue", "navy", "azure", "cobalt", "sapphire", "indigo", "cerulean", "prussian", "yinmn"]):
            return "Blue"
        # Green shades
        elif any(x in color for x in ["green", "olive", "emerald", "jade", "lime", "forest", "mint", "sage"]):
            return "Green"
        # Yellow shades
        elif any(x in color for x in ["yellow", "gold", "amber", "lemon", "canary", "mustard", "saffron"]):
            return "Yellow"
        # Orange shades
        elif any(x in color for x in ["orange", "coral", "peach", "tangerine", "apricot", "rust"]):
            return "Orange"
        # Purple shades
        elif any(x in color for x in ["purple", "violet", "lavender", "plum", "mauve", "lilac", "magenta", "orchid"]):
            return "Purple"
        # Pink shades
        elif any(x in color for x in ["pink", "rose", "salmon", "fuchsia", "blush"]):
            return "Pink"
        # Brown shades
        elif any(x in color for x in ["brown", "tan", "khaki", "chocolate", "coffee", "mocha", "umber", "liver", "sepia"]):
            return "Brown"
        else:
            return "Other"

    # Aggregate by date and color category
    color_price_by_date = {}

    for row in results:
        date = row['date']
        price = row['price_numeric']

        if row['colors']:
            try:
                colors = json.loads(row['colors'])
                # Use first/top color (or second for FashionBug tops as per previous logic)
                if colors:
                    color = colors[0]
                    category = categorize_color(color)

                    if date not in color_price_by_date:
                        color_price_by_date[date] = {}

                    if category not in color_price_by_date[date]:
                        color_price_by_date[date][category] = {'prices': [], 'count': 0}

                    color_price_by_date[date][category]['prices'].append(price)
                    color_price_by_date[date][category]['count'] += 1
            except:
                continue

    # Calculate averages and format for response
    data = []
    for date, categories in sorted(color_price_by_date.items()):
        date_entry = {'date': date}
        for category, info in categories.items():
            if info['prices']:
                avg_price = sum(info['prices']) / len(info['prices'])
                date_entry[category] = round(avg_price, 2)
                date_entry[f"{category}_count"] = info['count']
        data.append(date_entry)

    conn.close()
    return data


@app.get("/api/stats", response_model=StatsResponse)
def get_stats():
    """Get database statistics."""
    conn = get_db()
    cursor = conn.cursor()

    # Total products
    cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
    total_products = cursor.fetchone()[0]

    # Total sessions
    cursor.execute("SELECT COUNT(*) FROM scraping_sessions")
    total_sessions = cursor.fetchone()[0]

    # By site
    cursor.execute("""
        SELECT site, COUNT(*) as count
        FROM products
        WHERE is_active = 1
        GROUP BY site
    """)
    sites = {row['site']: row['count'] for row in cursor.fetchall()}

    # Price range
    cursor.execute("""
        SELECT MIN(price_numeric) as min_price, MAX(price_numeric) as max_price, AVG(price_numeric) as avg_price
        FROM price_history
        WHERE price_numeric IS NOT NULL
    """)
    price_data = cursor.fetchone()

    conn.close()

    return StatsResponse(
        total_products=total_products,
        total_sessions=total_sessions,
        sites=sites,
        price_range={
            "min": price_data['min_price'] or 0,
            "max": price_data['max_price'] or 0,
            "avg": price_data['avg_price'] or 0
        }
    )


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Starting Fashion Scraper API")
    print("=" * 60)
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
