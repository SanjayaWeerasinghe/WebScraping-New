"""Debug Fashion Bug collections page."""

import asyncio
from patchright.async_api import async_playwright


async def debug_fb():
    """Check Fashion Bug collections page."""
    url = "https://fashionbug.lk/collections/women?page=1"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size(dict(width=1920, height=1080))

        print(f"Loading {url}...")
        await page.goto(url, timeout=60000)
        await asyncio.sleep(4)

        # Scroll to trigger lazy loading
        for i in range(3):
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(0.8)

        # Try different selectors
        selectors = [
            '.product-item',
            '.product-card',
            '.product',
            'article.product',
            '.grid-item',
            '.product-grid-item',
            '[data-product]',
            '.card',
            '.item',
        ]

        print("\nTrying different selectors:")
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"  [FOUND] '{selector}' -> {len(elements)} elements")
                else:
                    print(f"  [EMPTY] '{selector}'")
            except Exception as e:
                print(f"  [ERROR] '{selector}' -> {e}")

        # Check if page is loading
        title = await page.title()
        print(f"\nPage title: {title}")

        # Get page HTML to check structure
        html = await page.content()
        if 'product' in html.lower():
            print("\n'product' found in HTML content")
        else:
            print("\n'product' NOT found in HTML - may need JavaScript rendering time")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_fb())
