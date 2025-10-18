"""Test the updated scraper with Fashion Bug and Thilaka Wardhana."""

import asyncio
from scraper_simple import SimpleFashionScraper


async def main():
    """Test scraper with specific sites."""
    scraper = SimpleFashionScraper(use_stealth=True)

    # Test only Fashion Bug and Thilaka Wardhana
    print("Testing Fashion Bug and Thilaka Wardhana for image URLs...\n")
    await scraper.scrape_all(site_keys=['fashionbug', 'thilakawardhana'])

    # Show results
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)

    for result in scraper.results:
        print(f"\n{result.site_name}:")
        print(f"  Total products: {result.total_products}")

        if result.products:
            print(f"\n  Sample products:")
            for p in result.products[:3]:
                print(f"    - {p.name}")
                print(f"      Price: {p.price}")
                img_preview = p.image_url[:80] + "..." if p.image_url and len(p.image_url) > 80 else p.image_url
                print(f"      Image: {img_preview}")

    # Save results
    scraper.save_results(output_format="json")

    print("\nTest complete! Check the output/ directory for results.")


if __name__ == "__main__":
    asyncio.run(main())
