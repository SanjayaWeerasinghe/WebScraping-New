"""Main scraper using Patchwright and AgentQL."""

import asyncio
import os
import re
from pathlib import Path
from typing import List, Optional, Dict
import json

from playwright.async_api import async_playwright, Page
import agentql
from patchright.async_api import async_playwright as async_patchwright

from models import Product, ScrapingResult, CategoryInfo
from config import (
    SITES, HEADLESS, TIMEOUT, WAIT_FOR_LOAD, OUTPUT_DIR,
    MAX_PRODUCTS_PER_CATEGORY, MAIN_CATEGORIES, CLOTHING_TYPES
)


class FashionScraper:
    """Scraper for fashion e-commerce sites using AgentQL."""

    def __init__(self, use_stealth: bool = True):
        self.use_stealth = use_stealth
        self.results = []

    async def scrape_site(self, site_key: str) -> ScrapingResult:
        """Scrape a single site."""
        site_config = SITES[site_key]
        print(f"\n{'='*60}")
        print(f"Scraping {site_config['name']} ({site_config['url']})")
        print(f"{'='*60}")

        products = []
        errors = []
        categories_scraped = []

        try:
            # Choose playwright implementation
            playwright_context = async_patchwright() if self.use_stealth else async_playwright()

            async with playwright_context as p:
                browser = await p.chromium.launch(headless=HEADLESS)
                page = await browser.new_page()
                await page.set_viewport_size({"width": 1920, "height": 1080})
                agentql_page = agentql.wrap(page)

                try:
                    # Navigate to site
                    print(f"Loading {site_config['url']}...")
                    await agentql_page.goto(site_config['url'], timeout=TIMEOUT, wait_until="networkidle")
                    await asyncio.sleep(WAIT_FOR_LOAD / 1000)

                    # Find and scrape categories
                    categories = await self._find_categories(agentql_page, site_config['name'])

                    print(f"\nFound {len(categories)} categories to scrape")

                    # Scrape each category
                    for category in categories:
                        print(f"\n[CATEGORY] Scraping: {category.parent_category} > {category.name}")
                        category_products = await self._scrape_category(
                            agentql_page,
                            category,
                            site_config['name']
                        )

                        if category_products:
                            products.extend(category_products)
                            categories_scraped.append(f"{category.parent_category}/{category.name}")
                            print(f"   [OK] Found {len(category_products)} products")

                    print(f"\n[SUCCESS] Total products scraped: {len(products)}")

                except Exception as e:
                    error_msg = f"Error scraping {site_config['name']}: {str(e)}"
                    print(f"[ERROR] {error_msg}")
                    errors.append(error_msg)

                finally:
                    await browser.close()

        except Exception as e:
            error_msg = f"Fatal error with {site_config['name']}: {str(e)}"
            print(f"[FATAL] {error_msg}")
            errors.append(error_msg)

        return ScrapingResult(
            site_name=site_config['name'],
            site_url=site_config['url'],
            products=products,
            total_products=len(products),
            categories_scraped=categories_scraped,
            errors=errors
        )

    async def _find_categories(self, page: Page, site_name: str) -> List[CategoryInfo]:
        """Find category links on the page."""
        categories = []

        # AgentQL query to find navigation menu with categories
        NAV_QUERY = """
        {
            navigation {
                women_link
                men_link
                kids_link
            }
        }
        """

        try:
            print("Looking for category navigation...")

            # Try to find main category links
            for main_cat in MAIN_CATEGORIES:
                # Look for category link using AgentQL
                CATEGORY_QUERY = f"""
                {{
                    {main_cat.lower()}_category {{
                        link
                        subcategories[] {{
                            name
                            link
                        }}
                    }}
                }}
                """

                try:
                    # For now, create a simple category list based on common patterns
                    # This will be refined when we actually test on the sites
                    category = CategoryInfo(
                        name=main_cat,
                        url=f"{main_cat.lower()}",  # Placeholder
                        parent_category=main_cat
                    )
                    categories.append(category)
                except Exception as e:
                    print(f"  Note: Could not find {main_cat} category: {e}")

        except Exception as e:
            print(f"Error finding categories: {e}")
            # Fallback: return basic categories
            for cat in MAIN_CATEGORIES:
                categories.append(CategoryInfo(name=cat, url="", parent_category=cat))

        return categories

    async def _scrape_category(self, page: Page, category: CategoryInfo, site_name: str) -> List[Product]:
        """Scrape products from a category page."""
        products = []

        # AgentQL query for products with categories and colors
        PRODUCT_QUERY = """
        {
            products[] {
                name
                price
                original_price
                sale_price
                colors[]
                color_options[]
                available_colors[]
                sizes[]
                size_options[]
                brand
                category
                product_type
                image
                product_image
                link
                product_link
                availability
                in_stock
            }
        }
        """

        try:
            print(f"  Querying products...")
            response = await page.query_elements(PRODUCT_QUERY)

            if response and hasattr(response, 'products'):
                product_elements = response.products[:MAX_PRODUCTS_PER_CATEGORY]

                for idx, elem in enumerate(product_elements, 1):
                    try:
                        # Extract product name
                        name = getattr(elem, 'name', '').strip() if hasattr(elem, 'name') else f"Product {idx}"

                        # Extract price (try multiple fields)
                        price = None
                        for price_field in ['price', 'sale_price']:
                            if hasattr(elem, price_field):
                                price = getattr(elem, price_field)
                                if price:
                                    break

                        # Extract original price
                        original_price = getattr(elem, 'original_price', None)

                        # Extract colors (try multiple fields)
                        colors = []
                        for color_field in ['colors', 'color_options', 'available_colors']:
                            if hasattr(elem, color_field):
                                field_value = getattr(elem, color_field)
                                if field_value:
                                    if isinstance(field_value, list):
                                        colors.extend([str(c) for c in field_value])
                                    else:
                                        colors.append(str(field_value))

                        # Extract sizes
                        sizes = []
                        for size_field in ['sizes', 'size_options']:
                            if hasattr(elem, size_field):
                                field_value = getattr(elem, size_field)
                                if field_value:
                                    if isinstance(field_value, list):
                                        sizes.extend([str(s) for s in field_value])
                                    else:
                                        sizes.append(str(field_value))

                        # Determine clothing type from product name or category
                        clothing_type = self._extract_clothing_type(name, getattr(elem, 'category', ''))

                        # Create product
                        product = Product(
                            name=name,
                            main_category=category.parent_category,
                            clothing_type=clothing_type,
                            price=price,
                            original_price=original_price,
                            colors=list(set(colors)),  # Remove duplicates
                            sizes=list(set(sizes)),
                            brand=getattr(elem, 'brand', None),
                            image_url=getattr(elem, 'image', None) or getattr(elem, 'product_image', None),
                            product_url=getattr(elem, 'link', None) or getattr(elem, 'product_link', None),
                            availability=getattr(elem, 'availability', None) or getattr(elem, 'in_stock', None),
                            site_name=site_name
                        )

                        products.append(product)
                        color_info = f", {len(product.colors)} colors" if product.colors else ""
                        print(f"    [+] {idx}. {product.name} - {product.price}{color_info}")

                    except Exception as e:
                        print(f"    [!] Error parsing product {idx}: {e}")
                        continue

            else:
                print("  No products found, trying alternative query...")
                products = await self._scrape_products_alternative(page, category, site_name)

        except Exception as e:
            print(f"  Error querying products: {e}")
            products = await self._scrape_products_alternative(page, category, site_name)

        return products

    async def _scrape_products_alternative(self, page: Page, category: CategoryInfo, site_name: str) -> List[Product]:
        """Alternative scraping method."""
        products = []

        # Simpler query structure
        ALT_QUERY = """
        {
            items[] {
                title
                product_title
                price_text
                current_price
                image_url
                thumbnail
            }
        }
        """

        try:
            response = await page.query_elements(ALT_QUERY)

            if response and hasattr(response, 'items'):
                for idx, item in enumerate(response.items[:MAX_PRODUCTS_PER_CATEGORY], 1):
                    name = getattr(item, 'title', None) or getattr(item, 'product_title', f'Product {idx}')
                    price = getattr(item, 'price_text', None) or getattr(item, 'current_price', None)
                    image = getattr(item, 'image_url', None) or getattr(item, 'thumbnail', None)

                    clothing_type = self._extract_clothing_type(name, category.name)

                    product = Product(
                        name=name,
                        main_category=category.parent_category,
                        clothing_type=clothing_type,
                        price=price,
                        image_url=image,
                        site_name=site_name
                    )
                    products.append(product)
                    print(f"    [+] (Alt) {idx}. {product.name}")

        except Exception as e:
            print(f"  Alternative method failed: {e}")

        return products

    def _extract_clothing_type(self, product_name: str, category_name: str) -> Optional[str]:
        """Extract clothing type from product name or category."""
        text = f"{product_name} {category_name}".lower()

        for clothing_type in CLOTHING_TYPES:
            if clothing_type.lower() in text:
                return clothing_type

        return None

    async def scrape_all(self, site_keys: Optional[List[str]] = None) -> List[ScrapingResult]:
        """Scrape all configured sites or specified sites."""
        if site_keys is None:
            site_keys = list(SITES.keys())

        print(f"\n>> Starting category-based scraping for {len(site_keys)} sites...")
        print(f">> Target categories: {', '.join(MAIN_CATEGORIES)}")

        # Scrape sites sequentially
        for site_key in site_keys:
            result = await self.scrape_site(site_key)
            self.results.append(result)

        return self.results

    def save_results(self, output_format: str = "json"):
        """Save scraping results to files."""
        output_path = Path(OUTPUT_DIR)
        output_path.mkdir(exist_ok=True)

        print(f"\n[SAVE] Saving results to {output_path}/...")

        for result in self.results:
            # Create filename-safe site name
            filename = result.site_name.lower().replace(" ", "_")

            if output_format == "json":
                filepath = output_path / f"{filename}.json"
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
                print(f"  [OK] Saved {filepath}")

            elif output_format == "csv":
                import pandas as pd
                filepath = output_path / f"{filename}.csv"
                if result.products:
                    df = pd.DataFrame([p.to_dict() for p in result.products])
                    df.to_csv(filepath, index=False, encoding='utf-8')
                    print(f"  [OK] Saved {filepath}")

        # Save combined results
        combined_file = output_path / "all_products.json"
        all_products = []
        for r in self.results:
            all_products.extend([p.to_dict() for p in r.products])

        combined_data = {
            "total_sites": len(self.results),
            "total_products": sum(r.total_products for r in self.results),
            "sites": [r.to_dict() for r in self.results]
        }

        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Saved combined results to {combined_file}")

        # Save combined CSV
        if all_products:
            import pandas as pd
            combined_csv = output_path / "all_products.csv"
            df = pd.DataFrame(all_products)
            df.to_csv(combined_csv, index=False, encoding='utf-8')
            print(f"  [OK] Saved {combined_csv}")

        print(f"\n[DONE] Total products scraped: {combined_data['total_products']}")


async def main():
    """Main function."""
    scraper = FashionScraper(use_stealth=True)

    # Scrape all sites
    await scraper.scrape_all()

    # Save results
    scraper.save_results(output_format="json")
    scraper.save_results(output_format="csv")


if __name__ == "__main__":
    asyncio.run(main())
