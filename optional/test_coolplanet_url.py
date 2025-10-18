"""Test Cool Planet URL parameters."""

import asyncio
from patchright.async_api import async_playwright

async def test_urls():
    """Test different URL parameter combinations."""

    test_urls = [
        ("Base URL", "https://coolplanet.lk/collections/shirts-t-shirts"),
        ("With page=1", "https://coolplanet.lk/collections/shirts-t-shirts?page=1"),
        ("With page=2", "https://coolplanet.lk/collections/shirts-t-shirts?page=2"),
        ("With limit=48", "https://coolplanet.lk/collections/shirts-t-shirts?limit=48"),
        ("With sort_by=best-selling", "https://coolplanet.lk/collections/shirts-t-shirts?sort_by=best-selling"),
        ("Combined: limit+sort", "https://coolplanet.lk/collections/shirts-t-shirts?limit=48&sort_by=best-selling"),
        ("Page 2 with params", "https://coolplanet.lk/collections/shirts-t-shirts?page=2&limit=48&sort_by=best-selling"),
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for name, url in test_urls:
            print(f"\n{'='*80}")
            print(f"{name}")
            print(f"URL: {url}")
            print('='*80)

            try:
                await page.goto(url, timeout=60000)
                await asyncio.sleep(4)

                # Scroll a bit
                await page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(1)

                # Count products
                products = await page.query_selector_all('.product-item')
                print(f"  Products found: {len(products)}")

                # Check for pagination
                next_btn = await page.query_selector('a[rel="next"], .pagination__next')
                print(f"  Next button exists: {next_btn is not None}")

                # Get first product name if available
                if products:
                    first_product = products[0]
                    name_elem = await first_product.query_selector('h2, h3, .product-title')
                    if name_elem:
                        product_name = await name_elem.inner_text()
                        print(f"  First product: {product_name.strip()[:50]}...")

            except Exception as e:
                print(f"  ERROR: {e}")

        await browser.close()

    print("\n" + "="*80)
    print("Test completed!")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_urls())
