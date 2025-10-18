"""
Import scraped product data from JSON files into SQLite database.
Handles price history, color history, and product tracking over time.
"""

import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime


DB_PATH = Path(__file__).parent / "fashion_scraper.db"
DATA_DIR = Path(__file__).parent / "output_with_colors"


def extract_price_numeric(price_str):
    """
    Extract numeric value from price string.

    Args:
        price_str: Price string like "Rs 1,850.00"

    Returns:
        Float value (e.g., 1850.00) or None
    """
    if not price_str:
        return None

    # Remove "Rs", "LKR", commas, and extra spaces
    cleaned = re.sub(r'[Rr]s|LKR|,', '', price_str).strip()

    # Extract first numeric value
    match = re.search(r'\d+\.?\d*', cleaned)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None

    return None


def import_json_file(file_path, session_id, cursor, scraped_at):
    """
    Import products from a single JSON file.

    Args:
        file_path: Path to JSON file
        session_id: Scraping session ID
        cursor: Database cursor
        scraped_at: Timestamp for this scrape

    Returns:
        Number of products imported
    """
    print(f"\n[+] Importing: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = data.get('products', [])
    print(f"    Found {len(products)} products")

    imported_count = 0
    updated_count = 0

    for product in products:
        # Skip products without URL
        if not product.get('product_url'):
            continue

        product_url = product['product_url']
        site = product.get('site_name', '')  # JSON uses 'site_name' not 'site'
        category = product.get('category', '')  # Will be extracted from filename if empty
        gender = product.get('main_category', '')  # 'Men' or 'Women'
        clothing_type = product.get('clothing_type', '')
        brand = product.get('brand', '')

        # Extract category from filename if not in product data
        # e.g., "cool_planet_men.json" -> category from filename
        if not category:
            filename = file_path.stem  # e.g., "cool_planet_men"
            parts = filename.split('_')
            if len(parts) >= 2:
                category = ' '.join(parts[2:]) if len(parts) > 2 else parts[-1]  # Get category part

        # Check if product exists
        cursor.execute("SELECT id, first_seen FROM products WHERE product_url = ?", (product_url,))
        result = cursor.fetchone()

        if result:
            # Product exists - update it
            product_id, first_seen = result
            cursor.execute("""
                UPDATE products
                SET last_seen = ?, is_active = 1, category = ?, gender = ?, clothing_type = ?, brand = ?
                WHERE id = ?
            """, (scraped_at, category, gender, clothing_type, brand, product_id))
            updated_count += 1
        else:
            # New product - insert it
            cursor.execute("""
                INSERT INTO products (product_url, site, category, gender, clothing_type, brand, first_seen, last_seen, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (product_url, site, category, gender, clothing_type, brand, scraped_at, scraped_at))
            product_id = cursor.lastrowid
            imported_count += 1

        # Insert product name
        name = product.get('name')
        if name:
            cursor.execute("""
                INSERT INTO product_names (product_id, name, scraped_at, session_id)
                VALUES (?, ?, ?, ?)
            """, (product_id, name, scraped_at, session_id))

        # Insert price
        price = product.get('price')
        if price:
            price_numeric = extract_price_numeric(price)
            cursor.execute("""
                INSERT INTO price_history (product_id, price, price_numeric, currency, scraped_at, session_id)
                VALUES (?, ?, ?, 'Rs', ?, ?)
            """, (product_id, price, price_numeric, scraped_at, session_id))

        # Insert colors
        colors = product.get('colors', [])
        if colors:
            colors_json = json.dumps(colors)
            cursor.execute("""
                INSERT INTO color_history (product_id, colors, colors_count, scraped_at, session_id)
                VALUES (?, ?, ?, ?, ?)
            """, (product_id, colors_json, len(colors), scraped_at, session_id))

        # Insert image URL
        image_url = product.get('image_url')
        if image_url:
            cursor.execute("""
                INSERT INTO image_history (product_id, image_url, scraped_at, session_id)
                VALUES (?, ?, ?, ?)
            """, (product_id, image_url, scraped_at, session_id))

        # Insert sizes
        sizes = product.get('sizes', [])
        if sizes:
            sizes_json = json.dumps(sizes)
            cursor.execute("""
                INSERT INTO size_history (product_id, sizes, scraped_at, session_id)
                VALUES (?, ?, ?, ?)
            """, (product_id, sizes_json, scraped_at, session_id))

    print(f"    New products: {imported_count}")
    print(f"    Updated products: {updated_count}")

    return len(products)


def import_all_data(data_dir=DATA_DIR, db_path=DB_PATH, notes=None):
    """
    Import all JSON files from the data directory into the database.

    Args:
        data_dir: Directory containing JSON files
        db_path: Path to SQLite database
        notes: Optional notes for this scraping session

    Returns:
        Session ID
    """
    print("=" * 60)
    print("Fashion Scraper Data Import")
    print("=" * 60)
    print(f"Database: {db_path}")
    print(f"Data directory: {data_dir}")

    # Check if database exists
    if not db_path.exists():
        print(f"\nERROR: Database not found at {db_path}")
        print("Please run init_database.py first!")
        return None

    # Check if data directory exists
    if not data_dir.exists():
        print(f"\nERROR: Data directory not found at {data_dir}")
        return None

    # Get all JSON files
    json_files = list(data_dir.glob("*.json"))
    if not json_files:
        print(f"\nERROR: No JSON files found in {data_dir}")
        return None

    print(f"\nFound {len(json_files)} JSON files to import:")
    for f in json_files:
        print(f"  - {f.name}")

    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create new scraping session
    started_at = datetime.now()
    cursor.execute("""
        INSERT INTO scraping_sessions (started_at, notes)
        VALUES (?, ?)
    """, (started_at, notes))
    session_id = cursor.lastrowid

    print(f"\nCreated scraping session #{session_id}")
    print(f"Started at: {started_at}")

    # Import each file
    total_products = 0
    for json_file in json_files:
        count = import_json_file(json_file, session_id, cursor, started_at)
        total_products += count

    # Update session
    completed_at = datetime.now()
    cursor.execute("""
        UPDATE scraping_sessions
        SET completed_at = ?, total_products = ?
        WHERE id = ?
    """, (completed_at, total_products, session_id))

    # Commit all changes
    conn.commit()

    # Display summary
    print("\n" + "=" * 60)
    print("Import Summary")
    print("=" * 60)

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products_db = cursor.fetchone()[0]
    print(f"Total products in database: {total_products_db}")

    cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
    active_products = cursor.fetchone()[0]
    print(f"Active products: {active_products}")

    cursor.execute("SELECT COUNT(*) FROM price_history")
    total_prices = cursor.fetchone()[0]
    print(f"Total price records: {total_prices}")

    cursor.execute("SELECT COUNT(*) FROM color_history")
    total_colors = cursor.fetchone()[0]
    print(f"Total color records: {total_colors}")

    print(f"\nSession #{session_id} completed at: {completed_at}")
    duration = (completed_at - started_at).total_seconds()
    print(f"Import duration: {duration:.2f} seconds")

    conn.close()

    print("\n" + "=" * 60)
    print("Import completed successfully!")
    print("=" * 60)

    return session_id


if __name__ == "__main__":
    # Import with current timestamp
    notes = input("Enter notes for this scraping session (optional): ").strip()
    if not notes:
        notes = None

    import_all_data(notes=notes)
