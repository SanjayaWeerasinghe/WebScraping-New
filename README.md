# Fashion E-commerce Web Scraper

A robust web scraper for Sri Lankan fashion e-commerce websites using **Patchwright** (stealth Playwright) with automatic pagination and intelligent product data extraction.

## Overview

This scraper collects comprehensive product data from Fashion Bug and Cool Planet, organizing products by gender categories (Men/Women) with automatic clothing type detection and image URL extraction.

## ✨ Features

- **Stealth Scraping** - Uses Patchwright to avoid bot detection
- **Automatic Pagination** - Navigates through multiple pages automatically (up to 10 pages per category)
- **Smart Image Extraction** - Handles lazy-loaded images and filters out payment gateway logos
- **Clothing Type Detection** - Automatically identifies shirts, trousers, tops, dresses, skirts, sarees, etc.
- **Category Organization** - Separates products by Men's and Women's categories
- **Multiple Output Formats** - Generates both JSON and CSV files
- **Robust Selectors** - Uses multiple fallback selectors for reliable data extraction

## 🎯 Supported Sites

- **Fashion Bug** (https://fashionbug.lk/)
- **Cool Planet** (https://coolplanet.lk/)

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `patchright` - Stealth version of Playwright
- `playwright` - Browser automation
- `pandas` - Data processing and CSV export
- `python-dotenv` - Environment configuration (optional)

### Step 2: Install Playwright Browsers

After installing the packages, install the Chromium browser:

```bash
playwright install chromium
```

If you encounter issues, force reinstall:

```bash
playwright install --force chromium
```

## 🚀 Usage

### Quick Start - Scrape Both Sites

Run the main category scraper to scrape both Fashion Bug and Cool Planet:

```bash
python scraper_categories.py
```

This will:
- Scrape Women's and Men's categories from both sites
- Navigate through pagination (up to 10 pages per category)
- Extract product names, prices, images, URLs, and clothing types
- Save results to `output/` directory

### Scrape Fashion Bug Only

```bash
python test_fashionbug.py
```

### Test Individual Sites

For debugging or testing:

```bash
python test_scraper.py
```

## 📊 Output Files

The scraper generates category-specific files in the `output/` directory:

### Fashion Bug
- `fashion_bug_women.json` - Women's products (JSON)
- `fashion_bug_women.csv` - Women's products (CSV)
- `fashion_bug_men.json` - Men's products (JSON)
- `fashion_bug_men.csv` - Men's products (CSV)

### Cool Planet
- `cool_planet_women.json` - Women's products (JSON)
- `cool_planet_women.csv` - Women's products (CSV)
- `cool_planet_men.json` - Men's products (JSON)
- `cool_planet_men.csv` - Men's products (CSV)

### Summary Report

Generate a summary of scraped data:

```bash
python scraping_summary.py
```

## 📋 Data Structure

Each product includes the following fields:

```json
{
  "name": "AMANI PRINTED SHIRT",
  "main_category": "Women",
  "clothing_type": "Shirt",
  "price": "Rs 2,890.00",
  "original_price": null,
  "colors": [],
  "sizes": [],
  "brand": null,
  "image_url": "https://fashionbug.lk/cdn/shop/files/...",
  "product_url": "https://fashionbug.lk/products/...",
  "availability": null,
  "description": null,
  "site_name": "Fashion Bug",
  "scraped_at": "2025-10-10T00:35:13.581582"
}
```

## 🎨 Clothing Types Detected

The scraper automatically identifies these clothing types from product names:

- **Shirts** - Formal shirts, casual shirts
- **T-Shirts** - T-shirts, tees
- **Blouses** - Women's blouses
- **Tops** - Casual tops, tube tops
- **Dresses** - Dresses, mini dresses
- **Frocks** - Traditional frocks
- **Skirts** - All skirt types
- **Trousers** - Pants, trousers
- **Shorts** - Casual shorts
- **Jeans** - Denim jeans
- **Sarees** - Traditional sarees

## ⚙️ Configuration

### Customize Category URLs

Edit `scraper_categories.py` to modify the categories scraped:

```python
FASHION_BUG_CATEGORIES = {
    "Women": [
        {"name": "Women's Clothing", "url": "https://fashionbug.lk/collections/women"},
    ],
    "Men": [
        {"name": "Men's Clothing", "url": "https://fashionbug.lk/collections/men"},
    ]
}
```

### Adjust Pagination

Change the maximum pages to scrape (default is 10):

```python
async def scrape_category_with_pagination(
    self,
    page,
    base_url: str,
    category_name: str,
    gender: str,
    max_pages: int = 10  # Change this number
)
```

### Headless Mode

By default, the scraper runs in headless mode (no browser window). To debug with visible browser:

In `scraper_categories.py`, change:

```python
browser = await p.chromium.launch(headless=True)  # Set to False
```

## 🔧 Project Structure

```
WebScraping/
├── scraper_categories.py      # Main scraper with pagination
├── models.py                  # Product data models
├── config.py                  # Site configurations
├── requirements.txt           # Python dependencies
├── organize_data.py          # Data cleaning and organization
├── scraping_summary.py       # Generate summary reports
├── test_fashionbug.py        # Test Fashion Bug scraping
├── test_scraper.py           # Test both sites
├── README.md                 # This file
└── output/                   # Generated data files
    ├── fashion_bug_women.json
    ├── fashion_bug_women.csv
    ├── fashion_bug_men.json
    ├── fashion_bug_men.csv
    ├── cool_planet_women.json
    ├── cool_planet_women.csv
    ├── cool_planet_men.json
    └── cool_planet_men.csv
```

## 🐛 Troubleshooting

### "No products found"

**Solution:**
1. Check your internet connection
2. Verify the website is accessible
3. Run with `headless=False` to see browser behavior
4. Check if website structure has changed

### Playwright Installation Issues

**Error:** `Executable doesn't exist`

**Solution:**
```bash
playwright install chromium
```

Or force reinstall:
```bash
playwright install --force chromium
```

### Image URLs Missing

The scraper automatically:
- Checks `src`, `srcset`, and `data-srcset` attributes
- Filters out payment gateway logos (mintpay, koko, payhere)
- Adds `https:` prefix to protocol-relative URLs

If images are still missing, the website may use background-image CSS or heavy JavaScript loading.

### Timeout Errors

If pages are loading slowly, increase wait times in `scraper_categories.py`:

```python
await asyncio.sleep(4)  # Increase this value
```

### Price Formatting Issues

Fashion Bug prices may include payment plan text. To clean prices:

```bash
python organize_data.py
```

This applies regex cleaning to extract just the base price (e.g., "Rs 3,390.00").

## 📈 Performance

**Current Results:**
- Fashion Bug: ~54 products (27 Women + 27 Men)
- Cool Planet: ~480 products (240 Women + 240 Men)
- **Total: 534 products**

**Speed:**
- ~3-5 seconds per page
- ~30-50 seconds per category
- Full scraping (both sites): ~2-3 minutes

## 🔍 Technical Details

### Image Extraction Logic

The scraper handles multiple image loading patterns:

1. Checks `srcset` attribute (primary for Fashion Bug)
2. Falls back to `data-srcset` for lazy-loaded images
3. Checks standard `src` attribute
4. Filters out payment logos by URL patterns
5. Adds `https:` protocol to relative URLs

### Selector Strategy

Uses multiple fallback selectors for robustness:

```python
selectors = ['.product-item', '.product-card', '.product', 'article.product']
```

Waits for elements with `state='attached'` instead of `visible` to handle Fashion Bug's lazy rendering.

### Pagination Detection

Automatically stops when:
- No products found on page
- No "next" button detected
- Maximum page limit reached

## ⚠️ Important Notes

- **Respect Robots.txt**: Always check website's robots.txt before scraping
- **Rate Limiting**: The scraper includes delays to avoid overwhelming servers
- **Legal Compliance**: Ensure you have permission to scrape the websites
- **Data Usage**: This data is for educational/research purposes only
- **Website Changes**: Websites may change structure; selectors may need updates

## 🤝 Contributing

To add a new website:

1. Add site configuration to `scraper_categories.py`
2. Test with a small category first
3. Verify image URLs and prices are extracted correctly
4. Update this README with the new site

## 📝 License

This project is for **educational purposes only**. Please respect website terms of service and local laws regarding web scraping.

## 🆘 Support

If you encounter issues:

1. Check the Troubleshooting section above
2. Run with `headless=False` to debug visually
3. Check if website HTML structure has changed
4. Verify all dependencies are installed correctly

## 📊 Sample Output

```json
{
  "site": "Fashion Bug",
  "category": "Women",
  "total_products": 27,
  "products": [
    {
      "name": "GIVO PRINTED TOP",
      "main_category": "Women",
      "clothing_type": "Top",
      "price": "Rs 1,390.00",
      "image_url": "https://fashionbug.lk/cdn/shop/files/...",
      "product_url": "https://fashionbug.lk/products/givo-printed-top",
      "site_name": "Fashion Bug",
      "scraped_at": "2025-10-10T00:35:13.630108"
    }
  ]
}
```

---

**Last Updated:** October 2025
**Version:** 1.0
**Author:** Web Scraping Project
