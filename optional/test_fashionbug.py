"""Test Fashion Bug scraping only."""

import asyncio
from scraper_categories import CategoryScraper, FASHION_BUG_CATEGORIES


async def main():
    """Test Fashion Bug only."""
    fb_scraper = CategoryScraper("Fashion Bug", FASHION_BUG_CATEGORIES)
    await fb_scraper.scrape_all_categories()
    fb_scraper.save_results()

    print("\n" + "="*80)
    print("FASHION BUG SCRAPING COMPLETE!")
    print("="*80)
    print(f"Total products: {len(fb_scraper.all_products)}")


if __name__ == "__main__":
    asyncio.run(main())
