"""Simplified scraper using Patchwright with standard Playwright selectors."""

import asyncio
import json
from pathlib import Path
from typing import List, Optional

from patchright.async_api import async_playwright

from models import Product, ScrapingResult
from config import SITES, HEADLESS, TIMEOUT, OUTPUT_DIR


class SimpleFashionScraper:
    """Simplified scraper using standard Playwright selectors."""

    def __init__(self, use_stealth: bool = True):
        self.use_stealth = use_stealth
        self.results = []

    async def scrape_site(self, site_key: str) -> ScrapingResult:
        """Scrape a single site."""
        site_config = SITES[site_key]
        print(f"\n{'='*60}")
        print(f"Scraping {site_config['name']} ({site_config['url']})")
        print(f"{'='*60}")

        products = []
        errors = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=HEADLESS)
                page = await browser.new_page()
                await page.set_viewport_size(dict(width=1920, height=1080))

                try:
                    print(f"Loading {site_config['url']}...")
                    await page.goto(site_config['url'], timeout=TIMEOUT)
                    await asyncio.sleep(3)

                    # Scroll down to trigger lazy loading
                    print("Scrolling to trigger lazy loading...")
                    for i in range(3):
                        await page.evaluate("window.scrollBy(0, 1000)")
                        await asyncio.sleep(1)
                    await page.evaluate("window.scrollTo(0, 0)")
                    await asyncio.sleep(2)

                    print("Scraping products from homepage...")
                    page_products = await self._scrape_products_from_page(page, site_config['name'])
                    products.extend(page_products)

                    print(f"\n[SUCCESS] Total products scraped: {len(products)}")

                except Exception as e:
                    error_msg = f"Error scraping {site_config['name']}: {str(e)}"
                    print(f"[ERROR] {error_msg}")
                    errors.append(error_msg)

                finally:
                    await browser.close()

        except Exception as e:
            error_msg = f"Fatal error with {site_config['name']}: {str(e)}"
            print(f"[FATAL] {error_msg}")
            errors.append(error_msg)

        return ScrapingResult(
            site_name=site_config['name'],
            site_url=site_config['url'],
            products=products,
            total_products=len(products),
            categories_scraped=[],
            errors=errors
        )

    async def _scrape_products_from_page(self, page, site_name: str) -> List[Product]:
        """Scrape products from current page using standard selectors."""
        products = []

        try:
            selectors = [
                '.product-item',
                '.product-card',
                '.product',
                'article.product',
                '.grid-item',
            ]

            product_elements = []
            for selector in selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    product_elements = await page.query_selector_all(selector)
                    if product_elements:
                        print(f"Found {len(product_elements)} products using selector '{selector}'")
                        break
                except:
                    continue

            if not product_elements:
                print("No products found with standard selectors")
                return products

            for idx, elem in enumerate(product_elements[:30], 1):
                try:
                    name_elem = await elem.query_selector('h2, h3, .product-title, .product-name')
                    name = await name_elem.inner_text() if name_elem else f"Product {idx}"
                    name = name.strip()

                    price_elem = await elem.query_selector('.price, .amount')
                    price = await price_elem.inner_text() if price_elem else None
                    if price:
                        price = price.strip()

                    # Get image URL - check all img tags and filter payment logos
                    img_elements = await elem.query_selector_all('img')
                    image_url = None

                    for img_elem in img_elements:
                        # Try src first
                        temp_url = await img_elem.get_attribute('src')

                        # If no src, try srcset (for lazy loading)
                        if not temp_url or temp_url == 'None':
                            srcset = await img_elem.get_attribute('srcset')
                            if srcset:
                                # Extract first URL from srcset
                                temp_url = srcset.split(',')[0].split(' ')[0].strip()

                        # If still no image, try data-srcset
                        if not temp_url or temp_url == 'None':
                            data_srcset = await img_elem.get_attribute('data-srcset')
                            if data_srcset:
                                temp_url = data_srcset.split(',')[0].split(' ')[0].strip()

                        # Skip payment logos, info icons, and invalid URLs
                        if temp_url and temp_url != 'None':
                            temp_lower = temp_url.lower()
                            # Skip payment/info icons and use product images only
                            skip_patterns = ['mintpay', 'koko', 'payment', 'payhere', 'logo', 'info_icon',
                                           'info.png', 'aliyuncs', 'd2zh3hh1z5w0qw']
                            if not any(x in temp_lower for x in skip_patterns):
                                image_url = temp_url
                                break

                    # Add https: prefix if needed
                    if image_url and image_url.startswith('//'):
                        image_url = 'https:' + image_url

                    link_elem = await elem.query_selector('a')
                    product_url = await link_elem.get_attribute('href') if link_elem else None
                    if product_url and not product_url.startswith('http'):
                        base_url = page.url.split('/')[0] + '//' + page.url.split('/')[2]
                        product_url = base_url + product_url

                    product = Product(
                        name=name,
                        price=price,
                        image_url=image_url,
                        product_url=product_url,
                        site_name=site_name
                    )

                    products.append(product)
                    print(f"  [+] {idx}. {product.name} - {product.price}")

                except Exception as e:
                    print(f"  [!] Error parsing product {idx}: {e}")
                    continue

        except Exception as e:
            print(f"Error scraping products: {e}")

        return products

    async def scrape_all(self, site_keys: Optional[List[str]] = None) -> List[ScrapingResult]:
        """Scrape all configured sites or specified sites."""
        if site_keys is None:
            site_keys = list(SITES.keys())

        print(f"\n>> Starting simplified scraping for {len(site_keys)} sites...")

        for site_key in site_keys:
            result = await self.scrape_site(site_key)
            self.results.append(result)

        return self.results

    def save_results(self, output_format: str = "json"):
        """Save scraping results to files."""
        output_path = Path(OUTPUT_DIR)
        output_path.mkdir(exist_ok=True)

        print(f"\n[SAVE] Saving results to {output_path}/...")

        for result in self.results:
            filename = result.site_name.lower().replace(" ", "_")

            if output_format == "json":
                filepath = output_path / f"{filename}_simple.json"
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
                print(f"  [OK] Saved {filepath}")

            elif output_format == "csv":
                import pandas as pd
                filepath = output_path / f"{filename}_simple.csv"
                if result.products:
                    df = pd.DataFrame([p.to_dict() for p in result.products])
                    df.to_csv(filepath, index=False, encoding='utf-8')
                    print(f"  [OK] Saved {filepath}")

        all_products = []
        for r in self.results:
            all_products.extend([p.to_dict() for p in r.products])

        combined_data = dict(
            total_sites=len(self.results),
            total_products=sum(r.total_products for r in self.results),
            sites=[r.to_dict() for r in self.results]
        )

        combined_file = output_path / "all_products_simple.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Saved combined results to {combined_file}")

        if all_products:
            import pandas as pd
            combined_csv = output_path / "all_products_simple.csv"
            df = pd.DataFrame(all_products)
            df.to_csv(combined_csv, index=False, encoding='utf-8')
            print(f"  [OK] Saved {combined_csv}")

        print(f"\n[DONE] Total products scraped: {combined_data['total_products']}")


async def main():
    """Main function."""
    scraper = SimpleFashionScraper(use_stealth=True)
    await scraper.scrape_all()
    scraper.save_results(output_format="json")
    scraper.save_results(output_format="csv")


if __name__ == "__main__":
    asyncio.run(main())
