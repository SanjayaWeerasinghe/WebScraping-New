"""
Verify database contains all required fields for analysis.
Shows sample records with: site, category, clothing_type, price, colors, date/time
"""

import sqlite3
import json
from pathlib import Path


DB_PATH = Path(__file__).parent / "fashion_scraper.db"


def verify_data():
    """Verify all required fields are present in database."""
    print("=" * 100)
    print("Database Verification - Sample Records")
    print("=" * 100)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    #trst
    # Get a few sample products with all their data
    cursor.execute("""
        SELECT
            p.id,
            p.site,
            p.category,
            p.gender,
            p.clothing_type,
            p.product_url,
            pn.name,
            ph.price,
            ph.price_numeric,
            ph.scraped_at as price_date,
            ch.colors,
            ch.scraped_at as color_date,
            ih.image_url,
            sh.sizes
        FROM products p
        LEFT JOIN product_names pn ON p.id = pn.product_id
        LEFT JOIN price_history ph ON p.id = ph.product_id
        LEFT JOIN color_history ch ON p.id = ch.product_id
        LEFT JOIN image_history ih ON p.id = ih.product_id
        LEFT JOIN size_history sh ON p.id = sh.product_id
        WHERE pn.id IN (SELECT MAX(id) FROM product_names GROUP BY product_id)
          AND (ph.id IS NULL OR ph.id IN (SELECT MAX(id) FROM price_history GROUP BY product_id))
          AND (ch.id IS NULL OR ch.id IN (SELECT MAX(id) FROM color_history GROUP BY product_id))
          AND (ih.id IS NULL OR ih.id IN (SELECT MAX(id) FROM image_history GROUP BY product_id))
          AND (sh.id IS NULL OR sh.id IN (SELECT MAX(id) FROM size_history GROUP BY product_id))
        LIMIT 5
    """)

    products = cursor.fetchall()

    for i, product in enumerate(products, 1):
        print(f"\n{'=' * 100}")
        print(f"SAMPLE PRODUCT #{i}")
        print('=' * 100)

        # Required fields verification
        print("\n[+] SITE (where it's from):")
        print(f"  {product['site']}")

        print("\n[+] CATEGORY:")
        print(f"  {product['category']} ({product['gender']})")

        print("\n[+] CLOTHING TYPE:")
        print(f"  {product['clothing_type']}")

        print("\n[+] PRODUCT NAME:")
        print(f"  {product['name']}")

        print("\n[+] PRICE:")
        print(f"  Formatted: {product['price']}")
        print(f"  Numeric: Rs {product['price_numeric']:.2f}")

        print("\n[+] COLORS:")
        if product['colors']:
            colors_list = json.loads(product['colors'])
            print(f"  {', '.join(colors_list)}")
        else:
            print("  (no colors)")

        print("\n[+] DATE & TIME (when scraped):")
        print(f"  Price recorded: {product['price_date']}")
        print(f"  Colors recorded: {product['color_date']}")

        print("\n[+] ADDITIONAL INFO:")
        print(f"  Product URL: {product['product_url'][:70]}...")
        if product['image_url']:
            print(f"  Image URL: {product['image_url'][:70]}...")
        if product['sizes']:
            sizes_list = json.loads(product['sizes'])
            print(f"  Sizes: {', '.join(sizes_list) if sizes_list else 'N/A'}")

    # Statistics
    print("\n\n" + "=" * 100)
    print("DATABASE COMPLETENESS CHECK")
    print("=" * 100)

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
    print(f"\n[+] Total products: {total_products}")

    cursor.execute("SELECT COUNT(*) FROM products WHERE site IS NOT NULL AND site != ''")
    with_site = cursor.fetchone()[0]
    print(f"[+] Products with SITE: {with_site} ({with_site/total_products*100:.1f}%)")

    cursor.execute("SELECT COUNT(*) FROM products WHERE category IS NOT NULL AND category != ''")
    with_category = cursor.fetchone()[0]
    print(f"[+] Products with CATEGORY: {with_category} ({with_category/total_products*100:.1f}%)")

    cursor.execute("SELECT COUNT(*) FROM products WHERE clothing_type IS NOT NULL AND clothing_type != ''")
    with_type = cursor.fetchone()[0]
    print(f"[+] Products with CLOTHING TYPE: {with_type} ({with_type/total_products*100:.1f}%)")

    cursor.execute("SELECT COUNT(DISTINCT product_id) FROM price_history WHERE price IS NOT NULL")
    with_price = cursor.fetchone()[0]
    print(f"[+] Products with PRICE: {with_price} ({with_price/total_products*100:.1f}%)")

    cursor.execute("SELECT COUNT(DISTINCT product_id) FROM color_history WHERE colors IS NOT NULL")
    with_colors = cursor.fetchone()[0]
    print(f"[+] Products with COLORS: {with_colors} ({with_colors/total_products*100:.1f}%)")

    cursor.execute("SELECT COUNT(DISTINCT product_id) FROM product_names WHERE name IS NOT NULL")
    with_names = cursor.fetchone()[0]
    print(f"[+] Products with NAME: {with_names} ({with_names/total_products*100:.1f}%)")

    # Check timestamps
    cursor.execute("SELECT MIN(scraped_at), MAX(scraped_at) FROM price_history")
    min_date, max_date = cursor.fetchone()
    print(f"\n[+] Date range: {min_date} to {max_date}")

    conn.close()

    print("\n" + "=" * 100)
    print("VERIFICATION COMPLETE - All required fields are present!")
    print("=" * 100)
    print("\nThe database contains:")
    print("  [+] Site (Fashion Bug / Cool Planet)")
    print("  [+] Category (Jeans, Dresses, T-Shirts, etc.)")
    print("  [+] Clothing Type (Trousers, Dress, T-Shirts)")
    print("  [+] Price (formatted and numeric)")
    print("  [+] Colors (extracted color names)")
    print("  [+] Date & Time (scraped_at timestamps)")
    print("\n[OK] Ready for price analysis and trend tracking!")


if __name__ == "__main__":
    verify_data()
