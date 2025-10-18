"""Organize scraped data into category-specific files with clean data."""

import json
import re
from pathlib import Path
import pandas as pd


def clean_price(price_text):
    """Extract clean price."""
    if not price_text:
        return None
    match = re.search(r'Rs\s*([\d,]+\.?\d*)', str(price_text))
    return f"Rs {match.group(1)}" if match else None


def detect_category(url, name):
    """Detect category from URL or name."""
    text = f"{url} {name}".lower()

    if any(word in text for word in ['women', 'ladies', 'womens', 'female', 'girl', 'saree', 'frock', 'blouse']):
        return 'Women'
    elif any(word in text for word in ['men', 'mens', 'male', 'gents', 'boy', 'jobbs']):
        return 'Men'
    elif any(word in text for word in ['kid', 'kids', 'children', 'child', 'baby']):
        return 'Kids'

    return 'Women'  # Default


def clean_image_url(url):
    """Filter out payment logos."""
    if not url:
        return None
    if any(x in url.lower() for x in ['mintpay', 'koko', 'payment', 'payhere', 'logo']):
        return None
    if url.startswith('//'):
        return 'https:' + url
    return url


def organize_file(input_file):
    """Organize a single JSON file by category."""
    print(f"\nProcessing: {input_file.name}")

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    site_name = data['site_name']
    site_name_clean = site_name.lower().replace(" ", "_")
    products = data['products']

    # Organize by category
    categorized = {'Women': [], 'Men': [], 'Kids': []}

    for p in products:
        # Clean price
        p['price'] = clean_price(p.get('price'))

        # Clean image
        p['image_url'] = clean_image_url(p.get('image_url'))

        # Detect category
        category = detect_category(p.get('product_url', ''), p.get('name', ''))
        p['main_category'] = category

        categorized[category].append(p)

    # Save each category
    output_path = input_file.parent
    for category, prods in categorized.items():
        if prods:
            filename = f"{site_name_clean}_{category.lower()}"

            # Save JSON
            json_file = output_path / f"{filename}.json"
            cat_data = {
                "site": site_name,
                "category": category,
                "total_products": len(prods),
                "products": prods
            }
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(cat_data, f, indent=2, ensure_ascii=False)

            # Save CSV
            csv_file = output_path / f"{filename}.csv"
            df = pd.DataFrame(prods)
            df.to_csv(csv_file, index=False, encoding='utf-8')

            print(f"  [OK] {filename}.json/.csv - {len(prods)} products")


def main():
    """Process all simple scraper output files."""
    output_dir = Path("output")

    # Find all *_simple.json files
    simple_files = list(output_dir.glob("*_simple.json"))

    print(f"Found {len(simple_files)} files to process")

    for file in simple_files:
        # Skip the combined file
        if file.name == "all_products_simple.json":
            continue

        try:
            organize_file(file)
        except Exception as e:
            print(f"  [ERROR] Failed to process {file.name}: {e}")

    print("\n[DONE] All files organized by category!")


if __name__ == "__main__":
    main()
