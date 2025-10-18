"""Final optimized scraper - scrapes homepage and categorizes products."""

import asyncio
import json
import re
from pathlib import Path
from typing import List, Optional, Dict

from patchright.async_api import async_playwright

from models import Product
from config import SITES, HEADLESS, TIMEOUT, OUTPUT_DIR, MAIN_CATEGORIES


class FinalFashionScraper:
    """Optimized scraper with proper categorization."""

    def __init__(self, use_stealth: bool = True):
        self.use_stealth = use_stealth
        self.results = {}
        self.page = None

    def clean_price(self, price_text: str) -> Optional[str]:
        """Extract main price from messy text."""
        if not price_text:
            return None
        match = re.search(r'Rs\s*([\d,]+\.?\d*)', price_text)
        return f"Rs {match.group(1)}" if match else None

    def detect_category(self, product_url: str, product_name: str) -> str:
        """Detect category from URL or name."""
        text = f"{product_url} {product_name}".lower()

        if any(word in text for word in ['women', 'ladies', 'womens', 'female', 'girl']):
            return 'Women'
        elif any(word in text for word in ['men', 'mens', 'male', 'gents', 'boy', 'jobbs']):
            return 'Men'
        elif any(word in text for word in ['kid', 'kids', 'children', 'child', 'baby']):
            return 'Kids'

        return 'Women'  # Default to Women

    async def get_colors_from_page(self, url: str) -> List[str]:
        """Extract colors from product page."""
        colors = []
        try:
            await self.page.goto(url, timeout=20000, wait_until="domcontentloaded")
            await asyncio.sleep(0.5)

            # Try to find color swatches or options
            color_elems = await self.page.query_selector_all('[class*="color"], [class*="swatch"], input[name*="Color"], input[name*="color"]')

            for elem in color_elems[:10]:
                try:
                    color = await elem.get_attribute('value')
                    if not color:
                        color = await elem.get_attribute('data-value')
                    if not color:
                        color = await elem.get_attribute('title')
                    if not color:
                        color = await elem.inner_text()

                    if color and color.strip() and len(color.strip()) < 30:
                        colors.append(color.strip())
                except:
                    pass

            # Remove duplicates
            colors = list(dict.fromkeys(colors))

        except:
            pass

        return colors[:10]

    async def scrape_site(self, site_key: str) -> Dict[str, List[Product]]:
        """Scrape site and organize by category."""
        site_config = SITES[site_key]
        print(f"\n{'='*60}")
        print(f"Scraping {site_config['name']}")
        print(f"{'='*60}")

        categorized_products = {cat: [] for cat in MAIN_CATEGORIES}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=HEADLESS)
                self.page = await browser.new_page()
                await self.page.set_viewport_size(dict(width=1920, height=1080))

                try:
                    print(f"Loading {site_config['url']}...")
                    await self.page.goto(site_config['url'], timeout=TIMEOUT, wait_until="networkidle")
                    await asyncio.sleep(3)

                    # Find product elements
                    selectors = ['.product-item', '.product-card', '.product', 'article.product']
                    product_elements = []

                    for selector in selectors:
                        try:
                            await self.page.wait_for_selector(selector, timeout=5000)
                            product_elements = await self.page.query_selector_all(selector)
                            if product_elements:
                                print(f"Found {len(product_elements)} products using '{selector}'")
                                break
                        except:
                            continue

                    if not product_elements:
                        print("No products found!")
                        return categorized_products

                    # Extract products
                    for idx, elem in enumerate(product_elements[:40], 1):
                        try:
                            # Name
                            name_elem = await elem.query_selector('h2, h3, .product-title, .product-name, a[href*="/products/"]')
                            name = await name_elem.inner_text() if name_elem else f"Product {idx}"
                            name = name.strip()

                            # Price
                            price_elem = await elem.query_selector('.price, [class*="price"]')
                            price_text = await price_elem.inner_text() if price_elem else None
                            price = self.clean_price(price_text) if price_text else None

                            # Image - Get ACTUAL product image, not payment logos
                            image_url = None
                            imgs = await elem.query_selector_all('img')
                            for img in imgs:
                                src = await img.get_attribute('src')
                                if src:
                                    # Skip payment logos
                                    if any(x in src.lower() for x in ['mintpay', 'koko', 'payment', 'payhere']):
                                        continue
                                    # Skip very small images (likely icons)
                                    width = await img.get_attribute('width')
                                    if width and int(width) < 50:
                                        continue

                                    # Make URL absolute
                                    if src.startswith('//'):
                                        image_url = 'https:' + src
                                    elif not src.startswith('http'):
                                        base = site_config['url'].rstrip('/')
                                        image_url = base + src
                                    else:
                                        image_url = src
                                    break

                            # Product URL
                            link_elem = await elem.query_selector('a[href*="/products/"]')
                            product_url = None
                            if link_elem:
                                href = await link_elem.get_attribute('href')
                                if href:
                                    if href.startswith('http'):
                                        product_url = href
                                    else:
                                        base = site_config['url'].rstrip('/')
                                        product_url = base + href

                            # Detect category
                            category = self.detect_category(product_url or '', name)

                            # Get colors (only for first 3 per category to save time)
                            colors = []
                            cat_count = len(categorized_products[category])
                            if product_url and cat_count < 3:
                                colors = await self.get_colors_from_page(product_url)
                                # Navigate back
                                await self.page.goto(site_config['url'], timeout=30000, wait_until="domcontentloaded")
                                await asyncio.sleep(1)

                            product = Product(
                                name=name,
                                main_category=category,
                                price=price,
                                colors=colors,
                                image_url=image_url,
                                product_url=product_url,
                                site_name=site_config['name']
                            )

                            categorized_products[category].append(product)

                            color_info = f", {len(colors)} colors" if colors else ""
                            print(f"  [{category}] {idx}. {name[:40]} - {price}{color_info}")

                        except Exception as e:
                            print(f"  [!] Error parsing product {idx}: {e}")

                except Exception as e:
                    print(f"[ERROR] {e}")

                finally:
                    await browser.close()

        except Exception as e:
            print(f"[FATAL] {e}")

        return categorized_products

    async def scrape_all(self, site_keys: Optional[List[str]] = None):
        """Scrape all sites."""
        if site_keys is None:
            site_keys = list(SITES.keys())

        print(f"\n>> Starting final scraping for {len(site_keys)} sites...")

        for site_key in site_keys:
            site_products = await self.scrape_site(site_key)
            self.results[site_key] = site_products

    def save_results(self):
        """Save results by site and category."""
        output_path = Path(OUTPUT_DIR)
        output_path.mkdir(exist_ok=True)

        print(f"\n[SAVE] Saving categorized results...")

        total = 0
        for site_key, categories in self.results.items():
            site_name = SITES[site_key]['name'].lower().replace(" ", "_")

            for category, products in categories.items():
                if products:
                    filename = f"{site_name}_{category.lower()}"

                    # JSON
                    json_file = output_path / f"{filename}.json"
                    data = {
                        "site": SITES[site_key]['name'],
                        "category": category,
                        "total": len(products),
                        "products": [p.to_dict() for p in products]
                    }
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"  [OK] {json_file} - {len(products)} products")

                    # CSV
                    try:
                        import pandas as pd
                        csv_file = output_path / f"{filename}.csv"
                        df = pd.DataFrame([p.to_dict() for p in products])
                        df.to_csv(csv_file, index=False, encoding='utf-8')
                        print(f"  [OK] {csv_file}")
                    except:
                        pass

                    total += len(products)

        print(f"\n[DONE] Total: {total} products across all categories")


async def main():
    scraper = FinalFashionScraper(use_stealth=True)
    await scraper.scrape_all()
    scraper.save_results()


if __name__ == "__main__":
    asyncio.run(main())
