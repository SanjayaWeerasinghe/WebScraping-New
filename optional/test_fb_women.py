"""Test script for Fashion Bug Women's category."""

import asyncio
from patchright.async_api import async_playwright

async def test_women():
    """Test Fashion Bug Women's category."""
    print("Starting browser...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.set_viewport_size(dict(width=1920, height=1080))

        url = "https://fashionbug.lk/collections/women"
        print(f"Loading {url}...")
        await page.goto(url, timeout=60000)
        await asyncio.sleep(4)

        # Close popups
        print("Checking for popups...")
        close_selectors = [
            '.halo-popup .close',
            '.newsletter-popup .close',
            'button[aria-label="Close"]',
            '.popup-close',
        ]
        for selector in close_selectors:
            try:
                close_btn = await page.query_selector(selector)
                if close_btn:
                    await close_btn.click()
                    print(f"Closed popup with selector: {selector}")
                    await asyncio.sleep(1)
                    break
            except:
                continue

        # Scroll down to load lazy content
        print("Initial scroll...")
        for i in range(5):
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(1)

        # Count initial products
        initial_count = len(await page.query_selector_all('.product-item, .product-card, .product'))
        print(f"Initial product count: {initial_count}")

        # Try clicking Show More multiple times
        for click_num in range(15):
            print(f"\n--- Attempt {click_num + 1} ---")

            # Look for Show More button
            show_more_selectors = [
                'button:has-text("Show more")',
                'a:has-text("Show more")',
                'button:has-text("Load more")',
                'a:has-text("Load more")',
            ]

            button = None
            for selector in show_more_selectors:
                try:
                    button = await page.wait_for_selector(selector, timeout=3000, state='visible')
                    if button:
                        print(f"Found button: {selector}")
                        break
                except:
                    continue

            if not button:
                print("No Show More button found!")
                break

            before_count = len(await page.query_selector_all('.product-item, .product-card, .product'))
            print(f"Products before click: {before_count}")

            # Click button
            try:
                await button.click(force=True, timeout=10000)
                print("Clicked!")
            except Exception as e:
                print(f"Click failed: {e}")
                break

            # Wait and scroll
            await asyncio.sleep(4)
            for i in range(3):
                await page.evaluate("window.scrollBy(0, 1500)")
                await asyncio.sleep(1)

            after_count = len(await page.query_selector_all('.product-item, .product-card, .product'))
            new_products = after_count - before_count
            print(f"Products after click: {after_count} (new: {new_products})")

            if new_products == 0:
                print("No new products loaded!")
                break

        final_count = len(await page.query_selector_all('.product-item, .product-card, .product'))
        print(f"\n=== FINAL COUNT: {final_count} products ===")

        print("\nWaiting 10 seconds before closing...")
        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_women())
