"""Test enhanced scraper on Fashion Bug."""

import asyncio
from scraper_enhanced import EnhancedFashionScraper


async def test():
    """Test scraping Fashion Bug with categories."""
    print("Testing enhanced scraper on Fashion Bug...")
    scraper = EnhancedFashionScraper(use_stealth=True)
    await scraper.scrape_all(site_keys=["fashionbug"])
    scraper.save_results()
    print("\nTest complete! Check output/ for category-specific files.")


if __name__ == "__main__":
    asyncio.run(test())
