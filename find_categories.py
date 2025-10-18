"""Find actual category URLs from Fashion Bug and Cool Planet navigation."""

import asyncio
from patchright.async_api import async_playwright


async def find_categories(url, site_name):
    """Extract category links from navigation."""
    print(f"\n{'='*80}")
    print(f"{site_name}")
    print(f"{'='*80}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size(dict(width=1920, height=1080))

        print(f"Loading {url}...")
        await page.goto(url, timeout=60000)
        await asyncio.sleep(3)

        # Get all links
        all_links = await page.query_selector_all('a')

        # Filter for collection/category links
        categories = {"Women": [], "Men": []}

        for link in all_links:
            href = await link.get_attribute('href')
            text = await link.inner_text()

            if href and text:
                href = href.strip()
                text = text.strip().lower()

                # Check for women's categories
                if any(word in text for word in ['women', 'ladies', 'womens', 'womans', 'woman', 'lady']):
                    if 'collection' in href or any(word in text for word in ['top', 'blouse', 'dress', 'skirt', 'trouser', 'pant', 'casual', 'shirt']):
                        categories["Women"].append({"text": text, "url": href})

                # Check for men's categories
                elif any(word in text for word in ['men', 'mens', 'gents', 'gent', 'male']):
                    if 'collection' in href or any(word in text for word in ['shirt', 'trouser', 'pant', 'short', 'casual', 'top']):
                        categories["Men"].append({"text": text, "url": href})

        # Remove duplicates
        for gender in categories:
            seen_urls = set()
            unique = []
            for cat in categories[gender]:
                if cat['url'] not in seen_urls:
                    seen_urls.add(cat['url'])
                    unique.append(cat)
            categories[gender] = unique

        # Print results
        for gender, cats in categories.items():
            if cats:
                print(f"\n{gender}'s Categories:")
                for cat in cats[:15]:  # Limit to first 15
                    print(f"  - {cat['text'][:40]:40} -> {cat['url']}")

        await browser.close()

        return categories


async def main():
    """Find categories from both sites."""
    fb_cats = await find_categories("https://fashionbug.lk/", "Fashion Bug")
    cp_cats = await find_categories("https://coolplanet.lk/", "Cool Planet")

    # Save to file for reference
    import json
    with open('discovered_categories.json', 'w', encoding='utf-8') as f:
        json.dump({
            "fashion_bug": fb_cats,
            "cool_planet": cp_cats
        }, f, indent=2, ensure_ascii=False)

    print("\n[SAVED] Category URLs saved to discovered_categories.json")


if __name__ == "__main__":
    asyncio.run(main())
