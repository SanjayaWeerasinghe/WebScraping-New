"""Quick diagnostic for Thilaka Wardhana images."""

import asyncio
from patchright.async_api import async_playwright


async def main():
    """Check Thilaka Wardhana image structure."""
    url = "https://thilakawardhana.com/"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size(dict(width=1920, height=1080))

        print(f"Loading {url}...")
        await page.goto(url, timeout=60000)
        await asyncio.sleep(5)

        # Find products
        selectors = ['.product-item', '.product-card', '.product', 'article.product', '.grid-item']
        product_elements = []

        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                product_elements = await page.query_selector_all(selector)
                if product_elements:
                    print(f"Found {len(product_elements)} products using: '{selector}'\n")
                    break
            except:
                continue

        if not product_elements:
            print("No products found!")
            await browser.close()
            return

        # Check first product
        elem = product_elements[0]
        img_elements = await elem.query_selector_all('img')
        print(f"First product has {len(img_elements)} img tags\n")

        for idx, img in enumerate(img_elements[:2], 1):
            print(f"Image {idx}:")
            src = await img.get_attribute('src')
            data_src = await img.get_attribute('data-src')
            srcset = await img.get_attribute('srcset')
            data_srcset = await img.get_attribute('data-srcset')

            print(f"  src: {src}")
            print(f"  data-src: {data_src}")
            print(f"  srcset: {srcset[:100] if srcset else None}")
            print(f"  data-srcset: {data_srcset[:100] if data_srcset else None}\n")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
