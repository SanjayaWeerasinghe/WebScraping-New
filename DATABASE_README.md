# Fashion Scraper Database System

SQLite database for tracking product prices, colors, and availability over time.

## Quick Start

### 1. Initialize Database (First Time Only)
```bash
py init_database.py
```

This creates `fashion_scraper.db` with all tables, indexes, and views.

### 2. Import Scraped Data
```bash
py import_to_database.py
```

Imports all JSON files from `output_with_colors/` directory. You'll be prompted to add optional notes for this scraping session.

### 3. Query and Analyze Data
```bash
py query_database.py
```

Interactive menu with options to:
- View scraping sessions
- Show price changes
- View database statistics
- Search products
- Show product history

## Database Schema

### Core Tables

**products** - Core product information
- `product_url` (unique identifier)
- `site`, `category`, `gender`, `clothing_type`, `brand`
- `first_seen`, `last_seen`, `is_active`

**scraping_sessions** - Track each scrape run
- `started_at`, `completed_at`, `total_products`, `notes`

### History Tables (Time-Series Data)

**product_names** - Track name changes
- Links to `product_id` and `session_id`
- Stores `name` and `scraped_at` timestamp

**price_history** - Track all price changes
- Stores both formatted price ("Rs 1,850.00") and numeric value (1850.00)
- Indexed by `product_id` and `scraped_at` for fast queries

**color_history** - Track color extraction results
- Stores colors as JSON array
- Links to scraping session

**image_history** - Track when product images change

**size_history** - Track size availability over time

### Views

**v_latest_products** - Shows current state of all active products

**v_price_changes** - Shows products with price differences between last two scrapes

## Workflow

### Regular Scraping Workflow

1. **Scrape new data**
   ```bash
   py scraper_categories.py
   ```

2. **Clean prices**
   ```bash
   py clean_prices.py
   ```

3. **Extract colors**
   ```bash
   py extract_colors.py
   ```

4. **Import to database**
   ```bash
   py import_to_database.py
   ```
   - Enter notes like "Weekly scrape" or "Black Friday prices"
   - Data is imported with current timestamp

5. **Analyze changes**
   ```bash
   py query_database.py
   ```
   - View price changes since last scrape
   - Track trends over time

### Example Queries

**Find products with biggest price drops:**
```python
import sqlite3
conn = sqlite3.connect('fashion_scraper.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT product_name, previous_price, current_price, price_change_percent
    FROM v_price_changes
    WHERE price_difference < 0
    ORDER BY price_change_percent ASC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(row)
```

**Track price history for specific product:**
```python
from query_database import show_product_history

# Using product ID
show_product_history(product_id=123)

# Or using URL
show_product_history(product_url="https://fashionbug.lk/products/...")
```

**Search products:**
```python
from query_database import search_products

search_products("shirt")  # Find all products with "shirt" in name
```

## Data Import Details

### Duplicate Handling
- Products identified by `product_url` (unique)
- On re-import:
  - Existing products: Updates `last_seen` timestamp, adds new price/color history
  - New products: Creates new product record
  - Disappeared products: `is_active` can be set to 0 manually

### Timestamp Strategy
- All history tables include `scraped_at` timestamp
- Enables time-series analysis
- Can track price changes week-over-week, month-over-month

### Session Tracking
- Each import creates a new `scraping_session` record
- All imported data links to this session
- Add notes to track special events ("Black Friday", "End of Season Sale", etc.)

## Current Database Stats

After initial import:
- **Total products**: 1,220 unique products
- **Price records**: 1,391 price points
- **Color records**: 1,414 color extractions
- **Sessions**: 1 (initial import)

## Files

- `init_database.py` - Database initialization script
- `import_to_database.py` - Import JSON data to database
- `query_database.py` - Interactive query tool
- `fashion_scraper.db` - SQLite database file (created after init)

## Tips

1. **Regular Scraping**: Run the complete workflow (scrape → clean → extract → import) weekly or monthly to build price history

2. **Notes**: Always add meaningful notes when importing:
   - "Weekly scrape - Oct 18"
   - "Black Friday sale"
   - "End of season clearance"

3. **Backup**: The database is a single file (`fashion_scraper.db`). Back it up regularly:
   ```bash
   copy fashion_scraper.db backups\fashion_scraper_2025-10-18.db
   ```

4. **Analysis**: After 2-3 scraping sessions, you'll be able to:
   - Track price trends
   - Identify seasonal patterns
   - Find best times to buy
   - Monitor stock availability

## Future Enhancements

- Export price trends to CSV/Excel
- Email alerts for price drops
- Web dashboard for visualization
- Automated scheduled scraping
