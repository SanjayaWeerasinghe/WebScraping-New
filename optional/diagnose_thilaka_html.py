"""Get actual HTML structure of Thilaka Wardhana product."""

import asyncio
from patchright.async_api import async_playwright


async def main():
    """Get HTML of Thilaka Wardhana product."""
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

        # Get HTML of first product
        if product_elements:
            elem = product_elements[0]
            html = await elem.evaluate("el => el.outerHTML")

            # Save to file for easier reading
            with open('thilaka_product.html', 'w', encoding='utf-8') as f:
                f.write(html)

            print("Saved HTML to thilaka_product.html")

            # Try to find product image with different selectors
            selectors_to_try = [
                '.product-image',
                '.product__image',
                '.product-card__image',
                '[data-product-image]',
                'picture',
                'picture img',
                '.card__media img',
                '.media img'
            ]

            print("\nTrying different image selectors:")
            for selector in selectors_to_try:
                img = await elem.query_selector(selector)
                if img:
                    src = await img.get_attribute('src')
                    data_src = await img.get_attribute('data-src')
                    srcset = await img.get_attribute('srcset')
                    print(f"\n[FOUND] {selector}:")
                    print(f"  src: {src}")
                    print(f"  data-src: {data_src}")
                    print(f"  srcset: {srcset[:80] if srcset else None}...")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
