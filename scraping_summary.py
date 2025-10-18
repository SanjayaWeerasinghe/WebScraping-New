"""Generate summary of scraped data."""

import json
from pathlib import Path


def main():
    """Generate summary of all scraped data."""
    output_dir = Path("output")

    print("\n" + "="*80)
    print("SCRAPING SUMMARY REPORT")
    print("="*80)

    # Files to check
    files_to_check = [
        "fashion_bug_women.json",
        "fashion_bug_men.json",
        "cool_planet_women.json",
        "cool_planet_men.json",
    ]

    total_products = 0
    site_totals = {}

    for filename in files_to_check:
        filepath = output_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            site = data['site']
            category = data['category']
            count = data['total_products']

            if site not in site_totals:
                site_totals[site] = 0
            site_totals[site] += count
            total_products += count

            print(f"\n{site} - {category}: {count} products")

            # Show sample clothing types
            clothing_types = {}
            for product in data['products']:
                ctype = product.get('clothing_type')
                if ctype:
                    clothing_types[ctype] = clothing_types.get(ctype, 0) + 1

            if clothing_types:
                print("  Clothing types:")
                for ctype, count in sorted(clothing_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"    - {ctype}: {count}")

    print("\n" + "="*80)
    print("SITE TOTALS")
    print("="*80)
    for site, count in site_totals.items():
        print(f"{site}: {count} products")

    print(f"\nGRAND TOTAL: {total_products} products")
    print("="*80)


if __name__ == "__main__":
    main()
