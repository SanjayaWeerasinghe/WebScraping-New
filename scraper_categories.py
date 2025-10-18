"""Category-specific scraper for Fashion Bug and Cool Planet with pagination."""

import asyncio
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from patchright.async_api import async_playwright

from models import Product


# Category configurations for each site
FASHION_BUG_CATEGORIES = {
    "Women": [
        {"name": "Jeans", "url": "https://fashionbug.lk/collections/jeans-women", "clothing_type": "Trousers"},
        {"name": "Pants", "url": "https://fashionbug.lk/collections/pants_ladies", "clothing_type": "Trousers"},
        {"name": "Skirts", "url": "https://fashionbug.lk/collections/skirt", "clothing_type": "Skirt"},
        {"name": "Dresses", "url": "https://fashionbug.lk/collections/dresses", "clothing_type": "Dress"},
        {"name": "Blouses & Shirts", "url": "https://fashionbug.lk/collections/blouses-shirts", "clothing_type": "Blouse"},
        {"name": "Crop Tops & T-Shirts", "url": "https://fashionbug.lk/collections/crop-tops-t-shirts", "clothing_type": "T-Shirt"},
    ],
    "Men": [
        {"name": "Casual Pants", "url": "https://fashionbug.lk/collections/casual-pants", "clothing_type": "Trousers"},
        {"name": "Jeans & Joggers", "url": "https://fashionbug.lk/collections/jeans-joggers-men", "clothing_type": "Trousers"},
        {"name": "T-Shirts & Polos", "url": "https://fashionbug.lk/collections/t-shirts-polos-men", "clothing_type": "T-Shirt"},
        {"name": "Casual Shirts", "url": "https://fashionbug.lk/collections/casual-shirts-men", "clothing_type": "Shirt"},
    ]
}

COOL_PLANET_CATEGORIES = {
    "Women": [
        {"name": "T-Shirts & Tops", "url": "https://coolplanet.lk/collections/t-shirts-tops", "clothing_type": "T-Shirt"},
        {"name": "Tops", "url": "https://coolplanet.lk/collections/tops", "clothing_type": "Top"},
        {"name": "Blouses", "url": "https://coolplanet.lk/collections/blouse", "clothing_type": "Blouse"},
        {"name": "Dresses", "url": "https://coolplanet.lk/collections/dresses", "clothing_type": "Dress"},
        {"name": "Pants", "url": "https://coolplanet.lk/collections/pants-1", "clothing_type": "Trousers"},
        {"name": "Skirts", "url": "https://coolplanet.lk/collections/skirts", "clothing_type": "Skirt"},
    ],
    "Men": [
        {"name": "T-Shirts", "url": "https://coolplanet.lk/collections/shirts-t-shirts", "clothing_type": "T-Shirt"},
        {"name": "Shirts", "url": "https://coolplanet.lk/collections/shirts", "clothing_type": "Shirt"},
        {"name": "Pants", "url": "https://coolplanet.lk/collections/pants", "clothing_type": "Trousers"},
    ]
}


class CategoryScraper:
    """Scraper focused on specific clothing categories with pagination."""

    def __init__(self, site_name: str, categories: dict):
        self.site_name = site_name
        self.categories = categories
        self.all_products = []

    def detect_clothing_type(self, name: str) -> Optional[str]:
        """Detect clothing type from product name."""
        if not name:
            return None

        name_lower = name.lower()

        # Define clothing type keywords
        clothing_types = {
            "Shirt": ["shirt"],
            "T-Shirt": ["t-shirt", "t shirt", "tshirt"],
            "Blouse": ["blouse"],
            "Top": ["top"],
            "Dress": ["dress"],
            "Frock": ["frock"],
            "Skirt": ["skirt"],
            "Trousers": ["trouser", "pant"],
            "Shorts": ["short"],
            "Jeans": ["jean"],
            "Saree": ["saree", "sari"],
        }

        # Check for each clothing type
        for clothing_type, keywords in clothing_types.items():
            if any(keyword in name_lower for keyword in keywords):
                return clothing_type

        return None

    async def scrape_all_categories(self):
        """Scrape all categories for this site."""
        print(f"\n{'='*80}")
        print(f"SCRAPING {self.site_name.upper()}")
        print(f"{'='*80}\n")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_viewport_size(dict(width=1920, height=1080))

            for gender, category_list in self.categories.items():
                print(f"\n--- {gender} ---")

                for category in category_list:
                    print(f"\nScraping: {category['name']}...")
                    try:
                        # Get clothing type from category config (if available)
                        clothing_type = category.get('clothing_type', None)

                        # Use different scraping strategy based on site
                        if "Fashion Bug" in self.site_name:
                            products = await self.scrape_with_show_more(
                                page,
                                category['url'],
                                category['name'],
                                gender,
                                clothing_type
                            )
                        else:
                            # Cool Planet and others use pagination
                            products = await self.scrape_category_with_pagination(
                                page,
                                category['url'],
                                category['name'],
                                gender,
                                clothing_type
                            )
                        print(f"  [OK] Got {len(products)} products from {category['name']}")
                        self.all_products.extend(products)
                    except Exception as e:
                        print(f"  [ERROR] Failed to scrape {category['name']}: {e}")

            await browser.close()

        print(f"\n[DONE] Total products: {len(self.all_products)}")
        return self.all_products

    async def scrape_with_show_more(
        self,
        page,
        url: str,
        category_name: str,
        gender: str,
        clothing_type: Optional[str] = None,
        max_clicks: int = 50
    ) -> List[Product]:
        """Scrape a category by clicking 'Show More' button repeatedly (for Fashion Bug)."""
        print(f"  Loading page...")

        # Try to load with maximum items per page if supported
        if '?' in url:
            url = f"{url}&grid_list=grid-view-50"
        else:
            url = f"{url}?grid_list=grid-view-50"

        await page.goto(url, timeout=60000)
        await asyncio.sleep(3)

        # Close any popups (newsletter, etc.)
        try:
            close_selectors = [
                '.halo-popup-close',
                '.halo-popup .close',
                '.newsletter-popup .close',
                'button[aria-label="Close"]',
                '.popup-close',
                '.modal-close',
                '[data-close-popup]',
                '.close-popup',
                'button.close',
            ]
            for selector in close_selectors:
                try:
                    close_btn = await page.query_selector(selector)
                    if close_btn and await close_btn.is_visible():
                        await close_btn.click()
                        print(f"  Closed popup with selector: {selector}")
                        await asyncio.sleep(1)
                        break
                except:
                    continue
        except Exception as e:
            pass  # No popup to close

        # Initial scroll to bottom to make sure Show More button appears
        print(f"  Scrolling to reveal Show More button...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

        clicks = 0
        consecutive_failures = 0
        max_consecutive_failures = 3

        while clicks < max_clicks and consecutive_failures < max_consecutive_failures:
            try:
                # Scroll to bottom to ensure button is visible
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)

                # Count products before clicking
                before_count = len(await page.query_selector_all('.product-item'))

                # Look for "Show More" button with various possible selectors
                show_more_selectors = [
                    'button.load-more__btn',
                    'button:has-text("Show more")',
                    'button:has-text("Show More")',
                    'a:has-text("Show more")',
                    'a:has-text("Show More")',
                    'button:has-text("Load more")',
                    '.load-more-btn',
                    '.load-more',
                    '.show-more',
                    '#show-more',
                    'button[class*="load"]',
                    'a[class*="load"]',
                ]

                button = None
                used_selector = None
                for selector in show_more_selectors:
                    try:
                        button = await page.wait_for_selector(selector, timeout=2000, state='attached')
                        if button:
                            # Check if button is visible and not disabled
                            is_visible = await button.is_visible()
                            is_enabled = await button.is_enabled()
                            if is_visible and is_enabled:
                                used_selector = selector
                                break
                            else:
                                button = None
                    except:
                        continue

                if not button:
                    print(f"  No more 'Show More' button found after {clicks} clicks")
                    break

                # Scroll button into view
                try:
                    await button.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                except:
                    pass

                # Click the button
                try:
                    await button.click(timeout=5000)
                except:
                    try:
                        # If regular click fails, try force click
                        await button.click(force=True, timeout=5000)
                    except:
                        try:
                            # If that fails too, use JavaScript click
                            await button.evaluate("el => el.click()")
                        except:
                            print(f"  Failed to click button")
                            consecutive_failures += 1
                            continue

                clicks += 1
                print(f"  Clicked 'Show More' ({used_selector}) - click {clicks}...", end=" ", flush=True)

                # Wait for loading to start
                await asyncio.sleep(1)

                # Wait for new products to appear - check multiple times
                max_wait = 10  # seconds
                waited = 0
                products_loaded = False

                while waited < max_wait:
                    current_count = len(await page.query_selector_all('.product-item'))
                    if current_count > before_count:
                        products_loaded = True
                        break
                    await asyncio.sleep(0.5)
                    waited += 0.5

                # Final count
                after_count = len(await page.query_selector_all('.product-item'))
                new_products = after_count - before_count

                if new_products > 0:
                    print(f"{new_products} new products loaded (total: {after_count})")
                    consecutive_failures = 0  # Reset failure counter
                else:
                    print(f"no new products (total: {after_count})")
                    consecutive_failures += 1

                # Small delay before next iteration
                await asyncio.sleep(1)

            except Exception as e:
                print(f"  Error during click {clicks + 1}: {e}")
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    break

        # Final scroll to load any lazy-loaded images
        print(f"  Final scroll to load all content...")
        for i in range(5):
            await page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {i/5})")
            await asyncio.sleep(0.5)

        # Now scrape all products from the page
        print(f"  Scraping all products from page...")
        products = await self.scrape_products_from_page(page, category_name, gender, clothing_type)

        return products

    async def scrape_category_with_pagination(
        self,
        page,
        base_url: str,
        category_name: str,
        gender: str,
        clothing_type: Optional[str] = None,
        max_pages: int = 10
    ) -> List[Product]:
        """Scrape a category with pagination support."""
        all_products = []
        page_num = 1

        # Add sort_by parameter for Cool Planet
        if '?' in base_url:
            base_url = f"{base_url}&sort_by=best-selling"
        else:
            base_url = f"{base_url}?sort_by=best-selling"

        while page_num <= max_pages:
            # Construct paginated URL
            if '?' in base_url:
                url = f"{base_url}&page={page_num}"
            else:
                url = f"{base_url}?page={page_num}"

            try:
                print(f"  Page {page_num}...", end=" ")
                await page.goto(url, timeout=60000)
                await asyncio.sleep(4)

                # Scroll to trigger lazy loading
                for i in range(3):
                    await page.evaluate("window.scrollBy(0, 1000)")
                    await asyncio.sleep(0.8)

                # Scrape products from this page
                products = await self.scrape_products_from_page(
                    page,
                    category_name,
                    gender,
                    clothing_type
                )

                if not products:
                    print("No products found, stopping pagination.")
                    break

                print(f"{len(products)} products")
                all_products.extend(products)

                # Check if there's a next page
                next_button = await page.query_selector('a[rel="next"], .pagination__next, .next')
                if not next_button:
                    print("  No more pages.")
                    break

                page_num += 1

            except Exception as e:
                print(f"Error on page {page_num}: {e}")
                break

        return all_products

    async def scrape_products_from_page(
        self,
        page,
        category_name: str,
        gender: str,
        clothing_type: Optional[str] = None
    ) -> List[Product]:
        """Scrape products from current page."""
        products = []

        try:
            # Wait for products to load
            selectors = ['.product-item', '.product-card', '.product', 'article.product']
            product_elements = []

            for selector in selectors:
                try:
                    await page.wait_for_selector(selector, timeout=10000, state='attached')
                    product_elements = await page.query_selector_all(selector)
                    if product_elements:
                        break
                except Exception as e:
                    continue

            if not product_elements:
                return products

            for elem in product_elements:
                try:
                    # Get product name - try multiple selectors
                    name = None
                    name_selectors = [
                        '.product-item__title',  # Cool Planet specific
                        'a.product-item__title',  # Cool Planet with tag
                        'h2',
                        'h3',
                        '.product-title',
                        '.product-name',
                        '.product__title',
                        'a.product-link',
                        'a[href*="/products/"]',  # Product link
                        '.card__heading',
                        '.card-title',
                        'a',  # Fallback to any link
                    ]

                    for selector in name_selectors:
                        try:
                            name_elem = await elem.query_selector(selector)
                            if name_elem:
                                temp_name = await name_elem.inner_text()
                                if temp_name and temp_name.strip() and len(temp_name.strip()) > 2:
                                    name = temp_name.strip()
                                    break
                        except:
                            continue

                    # Use provided clothing_type or detect from product name
                    if clothing_type is None:
                        product_clothing_type = self.detect_clothing_type(name) if name else None
                    else:
                        product_clothing_type = clothing_type

                    # Get price
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
                                temp_url = srcset.split(',')[0].split(' ')[0].strip()

                        # If still no image, try data-srcset
                        if not temp_url or temp_url == 'None':
                            data_srcset = await img_elem.get_attribute('data-srcset')
                            if data_srcset:
                                temp_url = data_srcset.split(',')[0].split(' ')[0].strip()

                        # Skip payment logos and invalid URLs
                        if temp_url and temp_url != 'None':
                            temp_lower = temp_url.lower()
                            skip_patterns = ['mintpay', 'koko', 'payment', 'payhere', 'logo',
                                           'info_icon', 'info.png', 'aliyuncs', 'd2zh3hh1z5w0qw']
                            if not any(x in temp_lower for x in skip_patterns):
                                image_url = temp_url
                                break

                    # Add https: prefix if needed
                    if image_url and image_url.startswith('//'):
                        image_url = 'https:' + image_url

                    # Get product URL
                    link_elem = await elem.query_selector('a')
                    product_url = await link_elem.get_attribute('href') if link_elem else None
                    if product_url and not product_url.startswith('http'):
                        base_url = page.url.split('/')[0] + '//' + page.url.split('/')[2]
                        product_url = base_url + product_url

                    # Create product
                    product = Product(
                        name=name,
                        main_category=gender,
                        clothing_type=product_clothing_type,
                        price=price,
                        image_url=image_url,
                        product_url=product_url,
                        site_name=self.site_name,
                        scraped_at=datetime.now().isoformat()
                    )

                    products.append(product)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"Error scraping page: {e}")

        return products

    def save_results(self, output_dir: str = "output"):
        """Save results to JSON and CSV files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        site_clean = self.site_name.lower().replace(" ", "_")

        # Organize by gender
        by_gender = {"Women": [], "Men": []}
        for product in self.all_products:
            if product.main_category in by_gender:
                by_gender[product.main_category].append(product)

        # Save each gender separately
        for gender, products in by_gender.items():
            if products:
                filename = f"{site_clean}_{gender.lower()}"

                # Save JSON
                json_file = output_path / f"{filename}.json"
                data = {
                    "site": self.site_name,
                    "category": gender,
                    "total_products": len(products),
                    "products": [p.to_dict() for p in products]
                }
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"  [SAVED] {json_file}")

                # Save CSV
                import pandas as pd
                csv_file = output_path / f"{filename}.csv"
                df = pd.DataFrame([p.to_dict() for p in products])
                df.to_csv(csv_file, index=False, encoding='utf-8')
                print(f"  [SAVED] {csv_file}")


async def main():
    """Main function to scrape both sites."""

    # Scrape Fashion Bug
    fb_scraper = CategoryScraper("Fashion Bug", FASHION_BUG_CATEGORIES)
    await fb_scraper.scrape_all_categories()
    fb_scraper.save_results()

    # Scrape Cool Planet
    cp_scraper = CategoryScraper("Cool Planet", COOL_PLANET_CATEGORIES)
    await cp_scraper.scrape_all_categories()
    cp_scraper.save_results()

    print("\n" + "="*80)
    print("ALL SCRAPING COMPLETE!")
    print("="*80)
    print(f"Fashion Bug: {len(fb_scraper.all_products)} products")
    print(f"Cool Planet: {len(cp_scraper.all_products)} products")
    print(f"Total: {len(fb_scraper.all_products) + len(cp_scraper.all_products)} products")


if __name__ == "__main__":
    asyncio.run(main())
