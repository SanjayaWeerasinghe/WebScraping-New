"""
Clean price data in JSON files.
Extract clean numeric price from messy scraped price strings.
"""

import json
import re
from pathlib import Path


def clean_price(price_str):
    """
    Extract clean price from messy price string.

    Args:
        price_str: Raw price string from scraping

    Returns:
        Clean price string (e.g., "Rs 1,850.00" or "1850.00")
    """
    if not price_str:
        return None

    # Remove newlines and extra whitespace
    price_str = ' '.join(price_str.split())

    # Pattern to match prices like "Rs 1,850.00" or "Rs 1850.00"
    # This will match the first occurrence of a price pattern
    patterns = [
        r'Rs\s*[\d,]+\.?\d*',  # Rs 1,850.00 or Rs 1850
        r'LKR\s*[\d,]+\.?\d*',  # LKR 1,850.00
        r'[\d,]+\.?\d*\s*Rs',   # 1,850.00 Rs
    ]

    for pattern in patterns:
        match = re.search(pattern, price_str, re.IGNORECASE)
        if match:
            price = match.group(0).strip()

            # Standardize format: "Rs 1,850.00"
            # Extract just the number part
            number_match = re.search(r'[\d,]+\.?\d*', price)
            if number_match:
                number = number_match.group(0)
                return f"Rs {number}"

    # If no pattern matched, try to extract any number
    number_match = re.search(r'[\d,]+\.?\d+', price_str)
    if number_match:
        return f"Rs {number_match.group(0)}"

    return None


def clean_prices_in_file(input_file, output_file=None):
    """
    Clean all prices in a JSON file.

    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file (if None, overwrites input)
    """
    if output_file is None:
        output_file = input_file

    print(f"\nCleaning prices in {input_file}...")

    # Load data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = data.get('products', [])
    cleaned_count = 0
    failed_count = 0

    # Clean each product's price
    for product in products:
        original_price = product.get('price')

        if original_price:
            cleaned_price = clean_price(original_price)

            if cleaned_price:
                product['price'] = cleaned_price
                cleaned_count += 1
            else:
                print(f"  Warning: Could not clean price: {original_price[:50]}...")
                failed_count += 1

        # Also clean original_price if it exists
        if product.get('original_price'):
            cleaned = clean_price(product.get('original_price'))
            if cleaned:
                product['original_price'] = cleaned

    # Save cleaned data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[+] Cleaned {cleaned_count} prices")
    if failed_count > 0:
        print(f"[!] Failed to clean {failed_count} prices")
    print(f"[+] Saved to: {output_file}")


def clean_all_files(directory, output_directory=None):
    """
    Clean prices in all JSON files in a directory.

    Args:
        directory: Directory containing JSON files
        output_directory: Output directory (if None, overwrites input files)
    """
    dir_path = Path(directory)
    json_files = list(dir_path.glob("*.json"))

    if not json_files:
        print(f"No JSON files found in {directory}")
        return

    print("="*60)
    print("Price Cleaning Utility")
    print("="*60)
    print(f"Found {len(json_files)} JSON files to process\n")

    for json_file in json_files:
        if output_directory:
            output_path = Path(output_directory)
            output_path.mkdir(exist_ok=True)
            output_file = output_path / json_file.name
        else:
            output_file = json_file

        clean_prices_in_file(json_file, output_file)

    print(f"\n{'='*60}")
    print("All files processed!")
    print("="*60)


if __name__ == "__main__":
    # Test with a few examples
    test_prices = [
        "Sale price\nRs 1,850.00\n        \n                 or 3 X Rs 1,072.66 with",
        "Rs 3,218.00\n        \n                 or 3 X Rs 1,072.66 with\n                \n                              \n                \n            or",
        "Rs 2,650.00",
        "LKR 5,000.00",
        "Sale price Rs 1,234.56",
    ]

    print("Testing price cleaning:")
    print("="*60)
    for price in test_prices:
        cleaned = clean_price(price)
        print(f"Original: {price[:50]}...")
        print(f"Cleaned:  {cleaned}")
        print()

    # Clean all files in output directory
    print("\n" + "="*60)
    print("Cleaning actual data files...")
    print("="*60)

    # Clean files in output directory
    clean_all_files("output")

    # Also clean files in output_with_colors if they exist
    if Path("output_with_colors").exists():
        print("\n" + "="*60)
        print("Cleaning output_with_colors directory...")
        print("="*60)
        clean_all_files("output_with_colors")
