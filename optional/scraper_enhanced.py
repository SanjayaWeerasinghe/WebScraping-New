"""Enhanced scraper with category detection, proper image extraction, and color scraping."""

import asyncio
import json
import re
from pathlib import Path
from typing import List, Optional, Dict

from patchright.async_api import async_playwright

from models import Product, ScrapingResult
from config import SITES, HEADLESS, TIMEOUT, OUTPUT_DIR, MAIN_CATEGORIES


class EnhancedFashionScraper:
    """Enhanced scraper with proper data extraction."""

    def __init__(self, use_stealth: bool = True):
        self.use_stealth = use_stealth
        self.results = {}  # Organized by site and category
        self.page = None

    def clean_price(self, price_text: str) -> Optional[str]:
        """Extract just the main price from text."""
        if not price_text:
            return None

        # Find first price pattern (Rs X,XXX.XX)
        match = re.search(r'Rs\s*([\d,]+\.?\d*)', price_text)
        if match:
            return f"Rs {match.group(1)}"
        return None

    def detect_category_from_url(self, url: str) -> Optional[str]:
        """Detect category from URL."""
        url_lower = url.lower()
        if 'women' in url_lower or 'ladies' in url_lower:
            return 'Women'
        elif 'men' in url_lower or 'mens' in url_lower or 'gents' in url_lower:
            return 'Men'
        elif 'kids' in url_lower or 'children' in url_lower:
            return 'Kids'
        return None

    def detect_category_from_name(self, name: str) -> Optional[str]:
        """Detect category from product name."""
        name_lower = name.lower()
        if 'women' in name_lower or 'ladies' in name_lower or 'womens' in name_lower:
            return 'Women'
        elif 'mens' in name_lower or 'men' in name_lower or 'gents' in name_lower:
            return 'Men'
        elif 'kids' in name_lower or 'children' in name_lower:
            return 'Kids'
        return None

    async def extract_colors_from_product_page(self, product_url: str, max_colors: int = 10) -> List[str]:
        """Visit product page and extract available colors."""
        colors = []
        try:
            await self.page.goto(product_url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(1)

            # Try multiple selectors for color options
            color_selectors = [
                '.color-swatch',
                '.swatch-element',
                '[data-option="Color"]',
                '.product-form__input input[type="radio"]',
                'input[name="Color"]',
                '.variant-input-wrap input',
            ]

            for selector in color_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        for elem in elements[:max_colors]:
                            color_value = await elem.get_attribute('value')
                            if not color_value:
                                color_value = await elem.get_attribute('data-value')
                            if not color_value:
                                color_value = await elem.get_attribute('title')
                            if not color_value:
                                label = await elem.query_selector('..') # parent
                                if label:
                                    color_value = await label.inner_text()

                            if color_value:
                                color_value = color_value.strip()
                                if color_value and color_value not in colors:
                                    colors.append(color_value)

                        if colors:
                            break
                except:
                    continue

        except Exception as e:
            print(f"    [!] Error extracting colors: {e}")

        return colors[:max_colors]

    async def scrape_category_page(self, category_url: str, category_name: str, site_name: str, limit: int = 20) -> List[Product]:
        """Scrape products from a specific category page."""
        products = []

        try:
            print(f"  Loading category: {category_name}")
            await self.page.goto(category_url, timeout=TIMEOUT, wait_until="networkidle")
            await asyncio.sleep(2)

            # Find product elements
            selectors = ['.product-item', '.product-card', '.product', 'article.product', '.grid-item']
            product_elements = []

            for selector in selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    product_elements = await self.page.query_selector_all(selector)
                    if product_elements:
                        print(f"  Found {len(product_elements)} products in {category_name}")
                        break
                except:
                    continue

            if not product_elements:
                print(f"  No products found in {category_name}")
                return products

            # Extract products
            for idx, elem in enumerate(product_elements[:limit], 1):
                try:
                    # Extract name
                    name_elem = await elem.query_selector('h2, h3, .product-title, .product-name, a[href*="/products/"]')
                    name = await name_elem.inner_text() if name_elem else f"Product {idx}"
                    name = name.strip()

                    # Extract price
                    price_elem = await elem.query_selector('.price, [class*="price"]')
                    price_text = await price_elem.inner_text() if price_elem else None
                    price = self.clean_price(price_text) if price_text else None

                    # Extract product image (not payment logos!)
                    image_url = None
                    img_elem = await elem.query_selector('img')
                    if img_elem:
                        src = await img_elem.get_attribute('src')
                        # Filter out payment gateway logos
                        if src and not any(x in src.lower() for x in ['mintpay', 'koko', 'payment', 'logo']):
                            if not src.startswith('http'):
                                src = 'https:' + src if src.startswith('//') else src
                            image_url = src

                    # Extract product URL
                    link_elem = await elem.query_selector('a[href*="/products/"]')
                    product_url = None
                    if link_elem:
                        href = await link_elem.get_attribute('href')
                        if href:
                            if not href.startswith('http'):
                                base_url = self.page.url.split('/')[0] + '//' + self.page.url.split('/')[2]
                                product_url = base_url + href
                            else:
                                product_url = href

                    # Try to get colors (only for first few products to save time)
                    colors = []
                    if product_url and idx <= 5:  # Get colors for first 5 products
                        colors = await self.extract_colors_from_product_page(product_url)
                        # Go back to category page
                        await self.page.goto(category_url, timeout=30000, wait_until="domcontentloaded")
                        await asyncio.sleep(1)

                    product = Product(
                        name=name,
                        main_category=category_name,
                        price=price,
                        colors=colors,
                        image_url=image_url,
                        product_url=product_url,
                        site_name=site_name
                    )

                    products.append(product)
                    color_info = f", {len(colors)} colors" if colors else ""
                    print(f"    [+] {idx}. {name[:50]} - {price}{color_info}")

                except Exception as e:
                    print(f"    [!] Error parsing product {idx}: {e}")
                    continue

        except Exception as e:
            print(f"  [ERROR] Failed to scrape {category_name}: {e}")

        return products

    async def scrape_site(self, site_key: str) -> Dict[str, List[Product]]:
        """Scrape a site organized by category."""
        site_config = SITES[site_key]
        print(f"\n{'='*60}")
        print(f"Scraping {site_config['name']} by categories")
        print(f"{'='*60}")

        site_products = {cat: [] for cat in MAIN_CATEGORIES}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=HEADLESS)
                self.page = await browser.new_page()
                await self.page.set_viewport_size(dict(width=1920, height=1080))

                try:
                    # Navigate to homepage first
                    print(f"Loading {site_config['url']}...")
                    await self.page.goto(site_config['url'], timeout=TIMEOUT, wait_until="networkidle")
                    await asyncio.sleep(2)

                    # Find category links
                    for category in MAIN_CATEGORIES:
                        category_url = None

                        # Try to find category link
                        category_patterns = [
                            f'a[href*="/{category.lower()}"]',
                            f'a[href*="/collections/{category.lower()}"]',
                            f'a:has-text("{category}")',
                        ]

                        for pattern in category_patterns:
                            try:
                                link = await self.page.query_selector(pattern)
                                if link:
                                    href = await link.get_attribute('href')
                                    if href:
                                        if not href.startswith('http'):
                                            base_url = site_config['url'].rstrip('/')
                                            category_url = base_url + href
                                        else:
                                            category_url = href
                                        break
                            except:
                                continue

                        if category_url:
                            products = await self.scrape_category_page(category_url, category, site_config['name'], limit=15)
                            site_products[category] = products
                        else:
                            print(f"  [!] Could not find {category} category link")

                except Exception as e:
                    print(f"[ERROR] Error scraping {site_config['name']}: {e}")

                finally:
                    await browser.close()

        except Exception as e:
            print(f"[FATAL] Fatal error with {site_config['name']}: {e}")

        return site_products

    async def scrape_all(self, site_keys: Optional[List[str]] = None):
        """Scrape all sites organized by category."""
        if site_keys is None:
            site_keys = list(SITES.keys())

        print(f"\n>> Starting enhanced category-based scraping for {len(site_keys)} sites...")

        for site_key in site_keys:
            site_products = await self.scrape_site(site_key)
            self.results[site_key] = site_products

        return self.results

    def save_results(self):
        """Save results organized by site and category."""
        output_path = Path(OUTPUT_DIR)
        output_path.mkdir(exist_ok=True)

        print(f"\n[SAVE] Saving results to {output_path}/...")

        for site_key, categories in self.results.items():
            site_name = SITES[site_key]['name']
            site_name_clean = site_name.lower().replace(" ", "_")

            # Save each category separately
            for category, products in categories.items():
                if products:
                    filename = f"{site_name_clean}_{category.lower()}"

                    # Save JSON
                    json_file = output_path / f"{filename}.json"
                    data = {
                        "site": site_name,
                        "category": category,
                        "total_products": len(products),
                        "products": [p.to_dict() for p in products]
                    }
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"  [OK] Saved {json_file} ({len(products)} products)")

                    # Save CSV
                    try:
                        import pandas as pd
                        csv_file = output_path / f"{filename}.csv"
                        df = pd.DataFrame([p.to_dict() for p in products])
                        df.to_csv(csv_file, index=False, encoding='utf-8')
                        print(f"  [OK] Saved {csv_file}")
                    except:
                        pass

        # Save combined summary
        total_products = sum(len(products) for site_products in self.results.values()
                           for products in site_products.values())
        print(f"\n[DONE] Total products scraped: {total_products}")


async def main():
    """Main function."""
    scraper = EnhancedFashionScraper(use_stealth=True)

    # Scrape all sites
    await scraper.scrape_all()

    # Save results
    scraper.save_results()


if __name__ == "__main__":
    asyncio.run(main())
