"""Diagnose image structure on Fashion Bug and Thilaka Wardhana."""

import asyncio
from patchright.async_api import async_playwright


async def diagnose_site(url, site_name):
    """Check how images are structured on a site."""
    print(f"\n{'='*60}")
    print(f"Diagnosing: {site_name}")
    print(f"URL: {url}")
    print(f"{'='*60}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.set_viewport_size(dict(width=1920, height=1080))

        print(f"Loading page...")
        await page.goto(url, timeout=60000)
        await asyncio.sleep(5)  # Let page fully load

        # Try different product selectors
        selectors = [
            '.product-item',
            '.product-card',
            '.product',
            'article.product',
            '.grid-item',
        ]

        product_elements = []
        used_selector = None

        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                product_elements = await page.query_selector_all(selector)
                if product_elements:
                    used_selector = selector
                    print(f"[OK] Found {len(product_elements)} products using: '{selector}'\n")
                    break
            except:
                continue

        if not product_elements:
            print("[ERROR] No products found!")
            await browser.close()
            return

        # Examine first 3 products in detail
        for idx, elem in enumerate(product_elements[:3], 1):
            print(f"\n--- Product {idx} ---")

            # Get the HTML of this product element
            html = await elem.evaluate("el => el.outerHTML")

            # Find all img tags
            img_elements = await elem.query_selector_all('img')
            print(f"Found {len(img_elements)} img tag(s)")

            for img_idx, img in enumerate(img_elements, 1):
                print(f"\n  Image {img_idx}:")

                # Check all possible image attributes
                src = await img.get_attribute('src')
                data_src = await img.get_attribute('data-src')
                srcset = await img.get_attribute('srcset')
                data_srcset = await img.get_attribute('data-srcset')
                loading = await img.get_attribute('loading')
                img_class = await img.get_attribute('class')

                print(f"    src: {src}")
                print(f"    data-src: {data_src}")
                print(f"    srcset: {srcset}")
                print(f"    data-srcset: {data_srcset}")
                print(f"    loading: {loading}")
                print(f"    class: {img_class}")

            # Also check for background images
            bg_elements = await elem.query_selector_all('[style*="background-image"]')
            if bg_elements:
                print(f"\n  Found {len(bg_elements)} elements with background-image")
                for bg_idx, bg in enumerate(bg_elements[:2], 1):
                    style = await bg.get_attribute('style')
                    print(f"    BG {bg_idx}: {style}")

        print("\n" + "="*60)

        input("\nPress Enter to close browser...")
        await browser.close()


async def main():
    """Diagnose both sites."""

    # Diagnose Fashion Bug
    await diagnose_site(
        "https://fashionbug.lk/",
        "Fashion Bug"
    )

    # Diagnose Thilaka Wardhana
    await diagnose_site(
        "https://thilakawardhana.com/",
        "Thilaka Wardhana"
    )


if __name__ == "__main__":
    asyncio.run(main())
