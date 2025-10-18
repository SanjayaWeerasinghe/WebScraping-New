"""
Initialize SQLite database for fashion scraper data.
Creates all tables, indexes, and views for tracking product data over time.
"""

import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path(__file__).parent / "fashion_scraper.db"


def init_database(db_path=DB_PATH):
    """
    Initialize the database schema.

    Args:
        db_path: Path to SQLite database file
    """
    print("=" * 60)
    print("Fashion Scraper Database Initialization")
    print("=" * 60)
    print(f"Database path: {db_path}")

    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Scraping Sessions
    print("\n[+] Creating scraping_sessions table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraping_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TIMESTAMP NOT NULL,
            completed_at TIMESTAMP,
            total_products INTEGER DEFAULT 0,
            notes TEXT
        )
    """)

    # Products
    print("[+] Creating products table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_url TEXT NOT NULL UNIQUE,
            site TEXT NOT NULL,
            category TEXT NOT NULL,
            gender TEXT,
            clothing_type TEXT,
            brand TEXT,
            first_seen TIMESTAMP NOT NULL,
            last_seen TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            CONSTRAINT unique_product_url UNIQUE(product_url)
        )
    """)

    # Indexes for products
    print("[+] Creating indexes on products...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_site_category ON products(site, category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_clothing_type ON products(clothing_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active)")

    # Product Names
    print("[+] Creating product_names table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            scraped_at TIMESTAMP NOT NULL,
            session_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES scraping_sessions(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_names_product_scraped ON product_names(product_id, scraped_at DESC)")

    # Price History
    print("[+] Creating price_history table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price TEXT NOT NULL,
            price_numeric REAL,
            currency TEXT DEFAULT 'Rs',
            scraped_at TIMESTAMP NOT NULL,
            session_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES scraping_sessions(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_product_scraped ON price_history(product_id, scraped_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_session ON price_history(session_id)")

    # Color History
    print("[+] Creating color_history table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS color_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            colors TEXT NOT NULL,
            colors_count INTEGER,
            scraped_at TIMESTAMP NOT NULL,
            session_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES scraping_sessions(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_color_history_product_scraped ON color_history(product_id, scraped_at DESC)")

    # Image History
    print("[+] Creating image_history table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            image_url TEXT NOT NULL,
            scraped_at TIMESTAMP NOT NULL,
            session_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES scraping_sessions(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_image_history_product_scraped ON image_history(product_id, scraped_at DESC)")

    # Size History
    print("[+] Creating size_history table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS size_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            sizes TEXT,
            scraped_at TIMESTAMP NOT NULL,
            session_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES scraping_sessions(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_size_history_product_scraped ON size_history(product_id, scraped_at DESC)")

    # Views
    print("[+] Creating v_latest_products view...")
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_latest_products AS
        SELECT
            p.id,
            p.product_url,
            p.site,
            p.category,
            p.gender,
            p.clothing_type,
            p.brand,
            (SELECT name FROM product_names WHERE product_id = p.id ORDER BY scraped_at DESC LIMIT 1) as current_name,
            (SELECT price FROM price_history WHERE product_id = p.id ORDER BY scraped_at DESC LIMIT 1) as current_price,
            (SELECT price_numeric FROM price_history WHERE product_id = p.id ORDER BY scraped_at DESC LIMIT 1) as current_price_numeric,
            (SELECT colors FROM color_history WHERE product_id = p.id ORDER BY scraped_at DESC LIMIT 1) as current_colors,
            (SELECT image_url FROM image_history WHERE product_id = p.id ORDER BY scraped_at DESC LIMIT 1) as current_image_url,
            (SELECT sizes FROM size_history WHERE product_id = p.id ORDER BY scraped_at DESC LIMIT 1) as current_sizes,
            p.first_seen,
            p.last_seen,
            p.is_active
        FROM products p
        WHERE p.is_active = 1
    """)

    print("[+] Creating v_price_changes view...")
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_price_changes AS
        SELECT
            p.id as product_id,
            p.product_url,
            p.site,
            p.category,
            (SELECT name FROM product_names WHERE product_id = p.id ORDER BY scraped_at DESC LIMIT 1) as product_name,
            ph1.price as current_price,
            ph1.price_numeric as current_price_numeric,
            ph1.scraped_at as current_scraped_at,
            ph2.price as previous_price,
            ph2.price_numeric as previous_price_numeric,
            ph2.scraped_at as previous_scraped_at,
            (ph1.price_numeric - ph2.price_numeric) as price_difference,
            ROUND(((ph1.price_numeric - ph2.price_numeric) / ph2.price_numeric * 100), 2) as price_change_percent
        FROM products p
        JOIN price_history ph1 ON p.id = ph1.product_id
        JOIN price_history ph2 ON p.id = ph2.product_id
        WHERE ph1.id = (SELECT id FROM price_history WHERE product_id = p.id ORDER BY scraped_at DESC LIMIT 1)
          AND ph2.id = (SELECT id FROM price_history WHERE product_id = p.id ORDER BY scraped_at DESC LIMIT 1 OFFSET 1)
          AND ph1.price_numeric != ph2.price_numeric
    """)

    # Commit changes
    conn.commit()

    # Display stats
    print("\n" + "=" * 60)
    print("Database initialized successfully!")
    print("=" * 60)

    # Show table count
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print(f"\nCreated {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
    views = cursor.fetchall()
    print(f"\nCreated {len(views)} views:")
    for view in views:
        print(f"  - {view[0]}")

    conn.close()
    print(f"\nDatabase file: {db_path}")
    print(f"File size: {db_path.stat().st_size / 1024:.2f} KB")


if __name__ == "__main__":
    init_database()
