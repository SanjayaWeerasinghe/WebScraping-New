"""Detailed diagnostic for all images in Thilaka Wardhana products."""

import asyncio
from patchright.async_api import async_playwright


async def main():
    """Check all images in Thilaka Wardhana product cards."""
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

        # Check first product in detail
        elem = product_elements[0]
        img_elements = await elem.query_selector_all('img')

        print(f"Product 1 has {len(img_elements)} img tags:")
        print("="*80)

        for idx, img in enumerate(img_elements, 1):
            src = await img.get_attribute('src')
            data_src = await img.get_attribute('data-src')
            srcset = await img.get_attribute('srcset')
            alt = await img.get_attribute('alt')
            img_class = await img.get_attribute('class')

            print(f"\nImage {idx}:")
            print(f"  src: {src}")
            print(f"  data-src: {data_src}")
            print(f"  srcset: {srcset[:100] if srcset else None}...")
            print(f"  alt: {alt}")
            print(f"  class: {img_class}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
