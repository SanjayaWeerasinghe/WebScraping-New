"""Check if Thilaka Wardhana uses background-image for products."""

import asyncio
from patchright.async_api import async_playwright


async def main():
    """Check for background images in Thilaka Wardhana products."""
    url = "https://thilakawardhana.com/"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size(dict(width=1920, height=1080))

        print(f"Loading {url}...")
        await page.goto(url, timeout=60000)
        await asyncio.sleep(5)

        product_elements = await page.query_selector_all('.product-item')
        print(f"Found {len(product_elements)} products\n")

        # Check first 2 products
        for pidx, elem in enumerate(product_elements[:2], 1):
            print(f"\n{'='*80}")
            print(f"Product {pidx}:")
            print('='*80)

            # Check for elements with background-image in style
            bg_elements = await elem.query_selector_all('[style*="background"]')
            if bg_elements:
                print(f"Found {len(bg_elements)} elements with background style:")
                for idx, bg in enumerate(bg_elements[:5], 1):
                    style = await bg.get_attribute('style')
                    tag_name = await bg.evaluate('el => el.tagName')
                    class_name = await bg.get_attribute('class')
                    print(f"\n  BG Element {idx} ({tag_name}):")
                    print(f"    class: {class_name}")
                    print(f"    style: {style}")

            # Also check for a tags with href (product links)
            a_elem = await elem.query_selector('a')
            if a_elem:
                href = await a_elem.get_attribute('href')
                print(f"\n  Product Link: {href}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
