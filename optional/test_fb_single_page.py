"""Test a single Fashion Bug page with detailed logging."""

import asyncio
from patchright.async_api import async_playwright
from models import Product
from datetime import datetime


async def test_single_page():
    """Test scraping a single Fashion Bug page."""
    url = "https://fashionbug.lk/collections/women?page=1"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size(dict(width=1920, height=1080))

        print(f"Loading {url}...")
        await page.goto(url, timeout=60000)
        await asyncio.sleep(4)

        print("Scrolling...")
        for i in range(3):
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(0.8)

        print("Looking for products...")

        # Try selectors
        selectors = ['.product-item', '.product-card', '.product', 'article.product']
        product_elements = []

        for selector in selectors:
            try:
                print(f"  Trying selector: {selector}")
                await page.wait_for_selector(selector, timeout=10000)
                product_elements = await page.query_selector_all(selector)
                if product_elements:
                    print(f"  [SUCCESS] Found {len(product_elements)} products with '{selector}'")
                    break
                else:
                    print(f"  [EMPTY] Selector '{selector}' returned no elements")
            except Exception as e:
                print(f"  [ERROR] Selector '{selector}': {e}")
                continue

        if not product_elements:
            print("[FAILED] No products found with any selector")
            await browser.close()
            return

        print(f"\nParsing {len(product_elements)} products...")
        products = []

        for idx, elem in enumerate(product_elements[:5], 1):
            try:
                # Get name
                name_elem = await elem.query_selector('h2, h3, .product-title, .product-name')
                name = await name_elem.inner_text() if name_elem else f"Product {idx}"
                print(f"  {idx}. {name.strip()[:50]}")

                products.append(name.strip())

            except Exception as e:
                print(f"  Error parsing product {idx}: {e}")

        print(f"\n[DONE] Successfully parsed {len(products)} products")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_single_page())
