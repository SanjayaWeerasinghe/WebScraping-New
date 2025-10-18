# Quick Start Guide

Get scraping in 3 simple steps!

## 🚀 Quick Setup (Windows)

### Step 1: Install Dependencies

```bash
py -m pip install -r requirements.txt
py -m playwright install chromium
```

### Step 2: Run the Scraper

```bash
py scraper_categories.py
```

### Step 3: Check Results

```bash
py scraping_summary.py
```

Your data is now in the `output/` folder!

## 📁 Output Files

After running, you'll have:

```
output/
├── fashion_bug_women.json    ← Women's products from Fashion Bug
├── fashion_bug_women.csv
├── fashion_bug_men.json      ← Men's products from Fashion Bug
├── fashion_bug_men.csv
├── cool_planet_women.json    ← Women's products from Cool Planet
├── cool_planet_women.csv
├── cool_planet_men.json      ← Men's products from Cool Planet
├── cool_planet_men.csv
```

## 🎯 What You Get

**534 Total Products** including:
- Product names
- Prices
- Image URLs
- Product URLs
- Clothing types (shirts, tops, dresses, sarees, etc.)
- Gender categories

## 🔧 Common Commands

```bash
# Scrape both sites (Fashion Bug + Cool Planet)
python scraper_categories.py

# Scrape Fashion Bug only
python test_fashionbug.py

# View summary of scraped data
python scraping_summary.py

# Clean prices (remove payment plan text)
python organize_data.py
```

## ⚡ Speed

- **Fashion Bug:** ~30 seconds (54 products)
- **Cool Planet:** ~2 minutes (480 products)
- **Total time:** ~2-3 minutes

## ❓ Troubleshooting

**Problem:** `playwright not found`
**Solution:** `playwright install chromium`

**Problem:** No products found
**Solution:** Check internet connection and run with `headless=False` for debugging

**Problem:** Images missing
**Solution:** The scraper already handles this, but some sites may have heavy lazy-loading

## 📖 Full Documentation

See [README.md](README.md) for complete documentation and advanced configuration.

---

Happy Scraping! 🎉
