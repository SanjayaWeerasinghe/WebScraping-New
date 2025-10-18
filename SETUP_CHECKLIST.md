# Setup Verification Checklist

Use this checklist to verify your scraper is set up correctly.

## ✅ Installation Checklist

### 1. Python Installation
- [ ] Python 3.8+ installed
- [ ] Can run `python --version` or `py --version`
- [ ] Can run `pip --version` or `py -m pip --version`

### 2. Dependencies Installed
- [ ] Ran `pip install -r requirements.txt`
- [ ] No error messages during installation
- [ ] Can import packages:
  ```python
  python -c "import patchright; print('✓ Patchright OK')"
  python -c "import pandas; print('✓ Pandas OK')"
  ```

### 3. Playwright Browsers
- [ ] Ran `playwright install chromium`
- [ ] No errors during browser installation
- [ ] Chromium browser installed successfully

## ✅ File Structure Checklist

Verify these files exist in your project:

```
D:\WebScraping\
├── [✓] scraper_categories.py   # Main scraper
├── [✓] models.py                # Data models
├── [✓] config.py                # Configuration
├── [✓] requirements.txt         # Dependencies
├── [✓] README.md                # Full documentation
├── [✓] QUICKSTART.md           # Quick setup guide
└── [✓] output/                  # Output folder (auto-created)
```

## ✅ First Run Checklist

### Test the Scraper

1. **Run Fashion Bug Test**
   ```bash
   python test_fashionbug.py
   ```
   - [ ] No errors
   - [ ] Created `output/fashion_bug_women.json`
   - [ ] Created `output/fashion_bug_men.json`
   - [ ] Products have image URLs
   - [ ] Products have prices

2. **Run Full Scraper**
   ```bash
   python scraper_categories.py
   ```
   - [ ] Scrapes Fashion Bug successfully
   - [ ] Scrapes Cool Planet successfully
   - [ ] No timeout errors
   - [ ] Creates all 8 output files (4 JSON + 4 CSV)

3. **Check Summary**
   ```bash
   python scraping_summary.py
   ```
   - [ ] Shows product counts
   - [ ] Shows clothing type breakdown
   - [ ] Total matches expected (~534 products)

## ✅ Output Validation

### Check Fashion Bug Data

Open `output/fashion_bug_women.json` and verify:

- [ ] Has product names
- [ ] Has prices (may include payment text)
- [ ] Has image URLs starting with `https://fashionbug.lk/`
- [ ] Has product URLs
- [ ] Has clothing_type field (Shirt/Top/Dress/Saree)
- [ ] ~27 products total

### Check Cool Planet Data

Open `output/cool_planet_women.json` and verify:

- [ ] Has product names
- [ ] Has image URLs starting with `https://coolplanet.lk/`
- [ ] Has product URLs
- [ ] ~240 products total

## 🐛 Common Issues & Solutions

### ❌ "playwright not found"
**Solution:**
```bash
playwright install chromium
```

### ❌ "ModuleNotFoundError: No module named 'patchright'"
**Solution:**
```bash
pip install -r requirements.txt
```

### ❌ "No products found"
**Solution:**
1. Check internet connection
2. Try with visible browser:
   - Edit `scraper_categories.py`
   - Change `headless=True` to `headless=False`
3. Check if websites are accessible in your region

### ❌ Timeout errors
**Solution:**
1. Increase timeout in `scraper_categories.py`:
   ```python
   await asyncio.sleep(4)  # Increase to 6 or 8
   ```
2. Check your internet speed

### ❌ Missing image URLs
**Solution:**
- For Fashion Bug: Should work with `srcset` extraction
- For Cool Planet: Should work with standard `src`
- If still missing, website structure may have changed

## 📊 Expected Results

After successful scraping:

```
Fashion Bug:
  Women: 27 products
    - Shirts: 14
    - Sarees: 5
    - Tops: 4
    - Dresses: 1
  Men: 27 products
    - Shirts: 24

Cool Planet:
  Women: 240 products
  Men: 240 products

Total: 534 products
```

## ✅ You're Ready!

If all checkboxes are ticked, your scraper is fully functional!

### Next Steps:

1. **Customize Categories**: Edit `scraper_categories.py` to add more categories
2. **Adjust Pagination**: Change `max_pages` to scrape more/less pages
3. **Clean Prices**: Run `organize_data.py` to clean price formatting
4. **Schedule Scraping**: Set up a cron job or scheduled task

## 📚 Resources

- **Full Documentation**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Playwright Docs**: https://playwright.dev/python/
- **Patchright Docs**: https://github.com/Kaliiiiiiiiii-Vinyzu/patchright

---

**Need Help?** Check the Troubleshooting section in README.md
