"""
Query and analyze fashion scraper database.
Provides utilities for price tracking, trend analysis, and product monitoring.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from tabulate import tabulate


DB_PATH = Path(__file__).parent / "fashion_scraper.db"


def get_connection(db_path=DB_PATH):
    """Get database connection."""
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        print("Please run init_database.py first!")
        return None

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def show_sessions():
    """Show all scraping sessions."""
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, started_at, completed_at, total_products, notes
        FROM scraping_sessions
        ORDER BY started_at DESC
    """)

    sessions = cursor.fetchall()

    if not sessions:
        print("No scraping sessions found.")
        conn.close()
        return

    print("\n" + "=" * 80)
    print("Scraping Sessions")
    print("=" * 80)

    headers = ["ID", "Started", "Completed", "Products", "Notes"]
    rows = []
    for s in sessions:
        rows.append([
            s['id'],
            s['started_at'],
            s['completed_at'] or "In progress",
            s['total_products'],
            s['notes'] or ""
        ])

    print(tabulate(rows, headers=headers, tablefmt="simple"))
    conn.close()


def show_price_changes(limit=20):
    """Show products with recent price changes."""
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT
            product_name,
            site,
            category,
            previous_price,
            current_price,
            price_difference,
            price_change_percent,
            current_scraped_at
        FROM v_price_changes
        ORDER BY ABS(price_change_percent) DESC
        LIMIT {limit}
    """)

    changes = cursor.fetchall()

    if not changes:
        print("\nNo price changes detected yet.")
        print("(You need at least 2 scraping sessions to see price changes)")
        conn.close()
        return

    print("\n" + "=" * 100)
    print(f"Top {limit} Price Changes")
    print("=" * 100)

    headers = ["Product", "Site", "Category", "Previous", "Current", "Change", "% Change", "Date"]
    rows = []
    for c in changes:
        change_indicator = "📈" if c['price_difference'] > 0 else "📉"
        rows.append([
            c['product_name'][:40] + "..." if len(c['product_name']) > 40 else c['product_name'],
            c['site'],
            c['category'],
            c['previous_price'],
            c['current_price'],
            f"{change_indicator} Rs {abs(c['price_difference']):.2f}",
            f"{c['price_change_percent']:+.1f}%",
            c['current_scraped_at'][:10]
        ])

    print(tabulate(rows, headers=headers, tablefmt="grid"))
    conn.close()


def show_product_history(product_id=None, product_url=None):
    """Show complete history for a specific product."""
    if not product_id and not product_url:
        print("ERROR: Provide either product_id or product_url")
        return

    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()

    # Get product info
    if product_id:
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    else:
        cursor.execute("SELECT * FROM products WHERE product_url = ?", (product_url,))

    product = cursor.fetchone()
    if not product:
        print("Product not found.")
        conn.close()
        return

    product_id = product['id']

    print("\n" + "=" * 80)
    print("Product Details")
    print("=" * 80)
    print(f"ID: {product['id']}")
    print(f"Site: {product['site']}")
    print(f"Category: {product['category']} ({product['gender']})")
    print(f"Clothing Type: {product['clothing_type']}")
    print(f"URL: {product['product_url']}")
    print(f"First seen: {product['first_seen']}")
    print(f"Last seen: {product['last_seen']}")
    print(f"Active: {'Yes' if product['is_active'] else 'No'}")

    # Get current name
    cursor.execute("""
        SELECT name FROM product_names
        WHERE product_id = ?
        ORDER BY scraped_at DESC LIMIT 1
    """, (product_id,))
    name = cursor.fetchone()
    if name:
        print(f"Name: {name['name']}")

    # Price history
    print("\n" + "-" * 80)
    print("Price History")
    print("-" * 80)
    cursor.execute("""
        SELECT price, price_numeric, scraped_at
        FROM price_history
        WHERE product_id = ?
        ORDER BY scraped_at DESC
    """, (product_id,))
    prices = cursor.fetchall()

    if prices:
        headers = ["Date", "Price", "Numeric"]
        rows = [[p['scraped_at'], p['price'], f"Rs {p['price_numeric']:.2f}"] for p in prices]
        print(tabulate(rows, headers=headers, tablefmt="simple"))

        # Calculate price stats
        if len(prices) > 1:
            min_price = min(p['price_numeric'] for p in prices if p['price_numeric'])
            max_price = max(p['price_numeric'] for p in prices if p['price_numeric'])
            current_price = prices[0]['price_numeric']

            print(f"\nPrice Range: Rs {min_price:.2f} - Rs {max_price:.2f}")
            if current_price == min_price:
                print("✅ Currently at LOWEST price!")
            elif current_price == max_price:
                print("⚠️ Currently at HIGHEST price!")
    else:
        print("No price history available.")

    # Color history
    print("\n" + "-" * 80)
    print("Color History")
    print("-" * 80)
    cursor.execute("""
        SELECT colors, scraped_at
        FROM color_history
        WHERE product_id = ?
        ORDER BY scraped_at DESC
        LIMIT 5
    """, (product_id,))
    colors = cursor.fetchall()

    if colors:
        for c in colors:
            colors_list = json.loads(c['colors'])
            print(f"{c['scraped_at']}: {', '.join(colors_list)}")
    else:
        print("No color history available.")

    conn.close()


def show_stats():
    """Show database statistics."""
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("Database Statistics")
    print("=" * 80)

    # Total products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
    print(f"Total products tracked: {total_products}")

    cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
    active_products = cursor.fetchone()[0]
    print(f"Active products: {active_products}")

    # By site
    print("\nProducts by Site:")
    cursor.execute("""
        SELECT site, COUNT(*) as count
        FROM products
        WHERE is_active = 1
        GROUP BY site
        ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row['site']}: {row['count']}")

    # By category
    print("\nTop 10 Categories:")
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM products
        WHERE is_active = 1
        GROUP BY category
        ORDER BY count DESC
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"  {row['category']}: {row['count']}")

    # Price records
    cursor.execute("SELECT COUNT(*) FROM price_history")
    total_prices = cursor.fetchone()[0]
    print(f"\nTotal price records: {total_prices}")

    # Average prices by category
    print("\nAverage Prices by Category (Top 10):")
    cursor.execute("""
        SELECT p.category, AVG(ph.price_numeric) as avg_price, COUNT(*) as count
        FROM products p
        JOIN price_history ph ON p.id = ph.product_id
        WHERE p.is_active = 1 AND ph.price_numeric IS NOT NULL
        GROUP BY p.category
        HAVING count > 5
        ORDER BY avg_price DESC
        LIMIT 10
    """)
    headers = ["Category", "Avg Price", "Products"]
    rows = [[row['category'], f"Rs {row['avg_price']:.2f}", row['count']] for row in cursor.fetchall()]
    print(tabulate(rows, headers=headers, tablefmt="simple"))

    conn.close()


def search_products(query, limit=20):
    """Search products by name."""
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            p.id,
            pn.name,
            p.site,
            p.category,
            p.clothing_type,
            ph.price,
            ph.price_numeric
        FROM products p
        LEFT JOIN product_names pn ON p.id = pn.product_id
        LEFT JOIN price_history ph ON p.id = ph.product_id
        WHERE pn.name LIKE ? AND p.is_active = 1
        AND pn.id IN (SELECT MAX(id) FROM product_names GROUP BY product_id)
        AND (ph.id IS NULL OR ph.id IN (SELECT MAX(id) FROM price_history GROUP BY product_id))
        ORDER BY pn.scraped_at DESC
        LIMIT ?
    """, (f"%{query}%", limit))

    products = cursor.fetchall()

    if not products:
        print(f"\nNo products found matching '{query}'")
        conn.close()
        return

    print("\n" + "=" * 100)
    print(f"Search Results for '{query}' ({len(products)} found)")
    print("=" * 100)

    headers = ["ID", "Name", "Site", "Category", "Type", "Price"]
    rows = []
    for p in products:
        rows.append([
            p['id'],
            p['name'][:50] + "..." if p['name'] and len(p['name']) > 50 else p['name'],
            p['site'],
            p['category'],
            p['clothing_type'],
            p['price'] or "N/A"
        ])

    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print(f"\nTip: Use show_product_history(product_id={products[0]['id']}) to see full history")

    conn.close()


def main_menu():
    """Interactive menu for database queries."""
    while True:
        print("\n" + "=" * 80)
        print("Fashion Scraper Database Query Tool")
        print("=" * 80)
        print("1. Show scraping sessions")
        print("2. Show price changes")
        print("3. Show database statistics")
        print("4. Search products")
        print("5. Show product history")
        print("6. Exit")
        print()

        choice = input("Select option (1-6): ").strip()

        if choice == "1":
            show_sessions()
        elif choice == "2":
            limit = input("Number of results to show (default 20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            show_price_changes(limit)
        elif choice == "3":
            show_stats()
        elif choice == "4":
            query = input("Enter search query: ").strip()
            if query:
                search_products(query)
        elif choice == "5":
            product_id = input("Enter product ID: ").strip()
            if product_id.isdigit():
                show_product_history(product_id=int(product_id))
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    # Check if tabulate is available
    try:
        import tabulate
    except ImportError:
        print("Installing tabulate for better table formatting...")
        import subprocess
        subprocess.run(["pip", "install", "tabulate"], check=True)
        from tabulate import tabulate

    main_menu()
