# Setup Instructions

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Step-by-Step Installation

### 1. Install pip (if not already installed)

If you get "No module named pip" error:

```bash
py -m ensurepip --upgrade
```

Or download get-pip.py:
```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
py get-pip.py
```

### 2. Install dependencies

```bash
py -m pip install playwright
py -m pip install patchright
py -m pip install agentql
py -m pip install python-dotenv
py -m pip install pandas
```

Or use requirements.txt:
```bash
py -m pip install -r requirements.txt
```

### 3. Install Playwright browsers

```bash
py -m playwright install chromium
```

### 4. (Optional) Set up AgentQL API key

If AgentQL requires an API key:

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   AGENTQL_API_KEY=your_api_key_here
   ```

## Running the Scraper

### Run all sites:
```bash
py scraper.py
```

### Test a single site first:

Edit `scraper.py` at the bottom:

```python
async def main():
    scraper = FashionScraper(use_stealth=True)

    # Test one site first
    await scraper.scrape_all(site_keys=["fashionbug"])

    scraper.save_results(output_format="json")
    scraper.save_results(output_format="csv")
```

## Troubleshooting

### Error: "No module named pip"
- Install pip using the instructions in Step 1 above

### Error: "playwright: command not found"
- Make sure you installed playwright browsers:
  ```bash
  py -m playwright install chromium
  ```

### Error: "No module named agentql"
- Install agentql:
  ```bash
  py -m pip install agentql
  ```

### No products scraped
- The sites may have changed their structure
- Try running with `HEADLESS = False` in `config.py` to see what's happening
- Check your internet connection

### AgentQL errors
- Check if you need an API key
- Visit https://docs.agentql.com/ for setup instructions

## What Gets Scraped

For each site, the scraper will attempt to extract:

- **Main Category**: Women, Men, Kids
- **Clothing Type**: Shirts, Trousers, Frocks, Sarees, Blouses, Skirts, etc.
- **Product Name**
- **Price** (current and original if on sale)
- **Colors** available
- **Sizes** available
- **Brand**
- **Images**
- **Product URLs**
- **Availability** status

## Output Files

Results are saved in the `output/` directory:

- `fashion_bug.json` / `fashion_bug.csv`
- `thilaka_wardhana.json` / `thilaka_wardhana.csv`
- `no_limit.json` / `no_limit.csv`
- `cool_planet.json` / `cool_planet.csv`
- `all_products.json` / `all_products.csv` (combined)

## Configuration

Edit `config.py` to customize:

```python
# Categories to scrape
MAIN_CATEGORIES = ["Women", "Men", "Kids"]

# Clothing types to identify
CLOTHING_TYPES = ["Shirts", "Trousers", "Frocks", "Sarees", ...]

# Scraping settings
HEADLESS = True  # Set to False to see browser
MAX_PRODUCTS_PER_CATEGORY = 30  # Limit products per category
```
