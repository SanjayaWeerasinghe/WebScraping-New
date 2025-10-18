"""Test simple scraper."""

import asyncio
from scraper_simple import SimpleFashionScraper


async def test():
    """Test scraping Fashion Bug."""
    print("Testing simplified scraper on Fashion Bug...")
    scraper = SimpleFashionScraper(use_stealth=True)
    await scraper.scrape_all(site_keys=["fashionbug"])
    scraper.save_results(output_format="json")
    scraper.save_results(output_format="csv")
    print("\nTest complete!")


if __name__ == "__main__":
    asyncio.run(test())
