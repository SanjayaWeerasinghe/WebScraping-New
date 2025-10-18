"""Test script for Fashion Bug Show More functionality."""

import asyncio
from patchright.async_api import async_playwright

async def test_show_more():
    """Test the show more button clicking."""
    print("Starting browser...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.set_viewport_size(dict(width=1920, height=1080))

        url = "https://fashionbug.lk/collections/women"
        print(f"Loading {url}...")
        await page.goto(url, timeout=60000)
        await asyncio.sleep(4)

        # Close any popups
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

        # Count initial products
        initial_count = len(await page.query_selector_all('.product-item, .product-card, .product'))
        print(f"Initial product count: {initial_count}")

        # Try to find show more button
        print("Looking for Show More button...")
        show_more_selectors = [
            'button:has-text("Show more")',
            'button:has-text("Load more")',
            'a:has-text("Show more")',
            '.load-more',
        ]

        button = None
        for selector in show_more_selectors:
            try:
                button = await page.wait_for_selector(selector, timeout=3000, state='visible')
                if button:
                    print(f"Found button with selector: {selector}")
                    break
            except:
                continue

        if button:
            print("Clicking Show More button...")
            try:
                await button.click(force=True, timeout=10000)
                print("Clicked!")
                await asyncio.sleep(3)

                new_count = len(await page.query_selector_all('.product-item, .product-card, .product'))
                print(f"Product count after click: {new_count}")
                print(f"New products loaded: {new_count - initial_count}")
            except Exception as e:
                print(f"Error clicking: {e}")
        else:
            print("No Show More button found!")

        print("\nWaiting 10 seconds before closing...")
        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_show_more())
