"""Test script to debug Cool Planet product name selectors."""

import asyncio
from patchright.async_api import async_playwright


async def test_selectors():
    """Test different selectors on Cool Planet page."""

    url = "https://coolplanet.lk/collections/shirts-t-shirts"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print(f"Loading: {url}")
        await page.goto(url, timeout=60000)

        # Scroll to trigger lazy loading
        print("Scrolling to load products...")
        for i in range(3):
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(1)

        await asyncio.sleep(3)

        # Get first product item - try many selectors
        product_selectors = [
            '.product-item',
            '.product-card',
            '.product',
            'article.product',
            '[class*="product"]',
            '.card',
            '.item',
            'div[class*="card"]',
        ]

        first_product = None
        for selector in product_selectors:
            try:
                first_product = await page.query_selector(selector)
                if first_product:
                    print(f"\n✓ Found product with selector: {selector}")
                    break
            except:
                continue

        if not first_product:
            print("ERROR: No product found with standard selectors!")
            print("\nLet me check what's actually on the page...")

            # List all elements with "product" or "card" in class name
            all_elements = await page.query_selector_all('[class*="product"], [class*="card"], [class*="item"]')
            print(f"Found {len(all_elements)} elements with product/card/item in class")

            if all_elements:
                for i, elem in enumerate(all_elements[:5]):  # Show first 5
                    class_name = await elem.get_attribute('class')
                    tag_name = await elem.evaluate('el => el.tagName')
                    print(f"  {i+1}. <{tag_name}> class='{class_name}'")

            input("\nPress Enter to close browser...")
            await browser.close()
            return

        # Test different name selectors
        name_selectors = [
            'h2',
            'h3',
            'h4',
            '.product-title',
            '.product-name',
            '.product__title',
            '.card-title',
            'a.product-link',
            '.title',
            '[class*="title"]',
            '[class*="name"]',
        ]

        print("\nTesting name selectors on first product:")
        print("="*60)

        for selector in name_selectors:
            try:
                elem = await first_product.query_selector(selector)
                if elem:
                    text = await elem.inner_text()
                    if text and text.strip():
                        print(f"✓ '{selector}' -> {text.strip()[:60]}")
                    else:
                        print(f"  '{selector}' -> (empty)")
                else:
                    print(f"  '{selector}' -> (not found)")
            except Exception as e:
                print(f"  '{selector}' -> ERROR: {e}")

        print("\n" + "="*60)
        print("Getting full HTML of first product for inspection:")
        print("="*60)

        html = await first_product.inner_html()
        print(html[:1000])  # First 1000 chars

        input("\nPress Enter to close browser...")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_selectors())
