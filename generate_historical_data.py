"""
Generate historical data for testing time-series charts.
Takes existing products and creates price/color history for the past 30 days
with randomly adjusted prices (5-25% variation).
"""

import sqlite3
import random
from datetime import datetime, timedelta
import json

DB_PATH = "fashion_scraper.db"
DAYS_TO_GENERATE = 30

def get_existing_data():
    """Get current products with their latest prices and colors."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all products with their current data
    cursor.execute("""
        SELECT
            p.id,
            p.product_url,
            p.site,
            p.gender,
            p.clothing_type,
            pn.name,
            ph.price,
            ph.price_numeric,
            ch.colors
        FROM products p
        LEFT JOIN product_names pn ON p.id = pn.product_id
        LEFT JOIN price_history ph ON p.id = ph.product_id
        LEFT JOIN color_history ch ON p.id = ch.product_id
        WHERE p.is_active = 1
          AND pn.id IN (SELECT MAX(id) FROM product_names GROUP BY product_id)
          AND ph.id IN (SELECT MAX(id) FROM price_history GROUP BY product_id)
          AND ch.id IN (SELECT MAX(id) FROM color_history GROUP BY product_id)
    """)

    products = cursor.fetchall()
    conn.close()

    return [dict(p) for p in products]

def generate_price_variation(base_price, day_offset):
    """
    Generate a price variation for a given day.
    - Earlier days have more variation
    - Random fluctuation between -25% and +25%
    - Ensure price is always positive
    """
    # Random variation between 5% and 25%
    variation_percent = random.uniform(0.05, 0.25)

    # Randomly increase or decrease
    if random.random() > 0.5:
        variation_percent = -variation_percent

    # Add some trend (prices generally increase over time)
    trend = (DAYS_TO_GENERATE - day_offset) * 0.002  # Slight upward trend

    new_price = base_price * (1 + variation_percent + trend)

    # Ensure price is positive and round to 2 decimals
    return max(100, round(new_price, 2))

def create_scraping_sessions(conn):
    """Create scraping sessions for the past 30 days."""
    cursor = conn.cursor()

    sessions = []
    now = datetime.now()

    for day in range(DAYS_TO_GENERATE, 0, -1):
        session_date = now - timedelta(days=day)

        cursor.execute("""
            INSERT INTO scraping_sessions (started_at, completed_at, total_products, notes)
            VALUES (?, ?, ?, ?)
        """, (
            session_date.strftime('%Y-%m-%d %H:%M:%S'),
            (session_date + timedelta(minutes=random.randint(15, 45))).strftime('%Y-%m-%d %H:%M:%S'),
            0,  # Will be updated later
            'Historical data generated for testing'
        ))

        sessions.append({
            'id': cursor.lastrowid,
            'date': session_date
        })

    conn.commit()
    return sessions

def populate_historical_data():
    """Main function to populate historical data."""
    print("=" * 60)
    print("Generating Historical Data for Testing")
    print("=" * 60)

    # Get existing data
    print("\n[1/4] Fetching existing product data...")
    products = get_existing_data()
    print(f"   Found {len(products)} products to replicate")

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create scraping sessions
    print("\n[2/4] Creating scraping sessions for past 30 days...")
    sessions = create_scraping_sessions(conn)
    print(f"   Created {len(sessions)} scraping sessions")

    # Generate historical data
    print("\n[3/4] Generating price and color history...")
    total_records = 0

    for day_offset, session in enumerate(sessions, 1):
        session_date = session['date']
        session_id = session['id']
        products_this_session = 0

        for product in products:
            # Generate price for this day
            new_price_numeric = generate_price_variation(product['price_numeric'], day_offset)
            new_price = f"Rs {new_price_numeric:,.2f}"

            # Insert price history
            cursor.execute("""
                INSERT INTO price_history (product_id, price, price_numeric, scraped_at, session_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                product['id'],
                new_price,
                new_price_numeric,
                session_date.strftime('%Y-%m-%d %H:%M:%S'),
                session_id
            ))

            # Insert color history (same colors)
            cursor.execute("""
                INSERT INTO color_history (product_id, colors, scraped_at, session_id)
                VALUES (?, ?, ?, ?)
            """, (
                product['id'],
                product['colors'],
                session_date.strftime('%Y-%m-%d %H:%M:%S'),
                session_id
            ))

            # Insert product name (same name)
            cursor.execute("""
                INSERT INTO product_names (product_id, name, scraped_at, session_id)
                VALUES (?, ?, ?, ?)
            """, (
                product['id'],
                product['name'],
                session_date.strftime('%Y-%m-%d %H:%M:%S'),
                session_id
            ))

            products_this_session += 1
            total_records += 3  # price + color + name

        # Update session product count
        cursor.execute("""
            UPDATE scraping_sessions
            SET total_products = ?
            WHERE id = ?
        """, (products_this_session, session_id))

        # Commit every 5 days to show progress
        if day_offset % 5 == 0:
            conn.commit()
            print(f"   Day {day_offset}/{DAYS_TO_GENERATE}: {products_this_session} products x 3 records")

    conn.commit()
    print(f"\n   Total records created: {total_records:,}")

    # Update product last_seen timestamps
    print("\n[4/4] Updating product timestamps...")
    cursor.execute("""
        UPDATE products
        SET last_seen = datetime('now')
        WHERE is_active = 1
    """)
    conn.commit()

    # Show statistics
    print("\n" + "=" * 60)
    print("Data Generation Complete!")
    print("=" * 60)

    cursor.execute("SELECT COUNT(*) FROM scraping_sessions")
    total_sessions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM price_history")
    total_prices = cursor.fetchone()[0]

    cursor.execute("""
        SELECT MIN(DATE(scraped_at)) as min_date, MAX(DATE(scraped_at)) as max_date
        FROM price_history
    """)
    date_range = cursor.fetchone()

    print(f"\nDatabase Statistics:")
    print(f"  - Total scraping sessions: {total_sessions}")
    print(f"  - Total price records: {total_prices:,}")
    print(f"  - Date range: {date_range['min_date']} to {date_range['max_date']}")
    print(f"  - Products tracked: {len(products)}")
    print(f"  - Average records per product: {total_prices / len(products):.1f}")

    conn.close()

    print("\nYou can now view the time-series charts at:")
    print("  http://localhost:8080/price-analysis")
    print("  http://localhost:8080/color-trends")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        populate_historical_data()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
