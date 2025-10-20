# Fashion Scraper Application

A comprehensive web scraping and analytics application for tracking fashion product data, prices, and color trends from competitor websites.

## Overview

This application combines web scraping, data processing, and analytics visualization to provide competitive intelligence for Sri Lankan fashion e-commerce. It tracks products from Fashion Bug and Cool Planet with automated scraping pipelines and real-time progress monitoring.

## Features

- **Stealth Web Scraping** - Uses Patchwright to avoid bot detection
- **Automated Pipeline** - Complete workflow from scraping to database import
- **Real-time Progress Tracking** - Live console output with step-by-step status
- **Price & Color Analytics** - Track trends over time with interactive charts
- **Product Timeline** - Monitor product launches and availability
- **REST API** - FastAPI backend with comprehensive endpoints
- **React Dashboard** - Modern UI with filtering and data visualization
- **Docker Support** - Single-command deployment with all dependencies

## Quick Start with Docker

### Prerequisites

- Docker installed on your system
- 4GB+ RAM available
- Port 8000 available

### Build the Docker Image

```bash
docker build -t fashion-scraper .
```

This will:
- Build the React frontend
- Install Python dependencies
- Package everything into a single image with the database

### Run the Application

```bash
docker run -p 8000:8000 fashion-scraper
```

### Access the Application

Once the container is running:

- **Frontend Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## Manual Setup (Without Docker)

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

3. Start the FastAPI server:
```bash
python api.py
```

The API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd FE
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:8080

## Running the Scraper

### Via Web Interface

1. Navigate to the landing page (http://localhost:8000)
2. Click the "Run Scraping" button
3. Monitor progress in the popup modal with real-time console output

### Via Command Line

Run the complete pipeline:
```bash
python run_scraping_pipeline.py
```

Or run individual steps:
```bash
python scraper_categories.py    # Step 1: Web scraping
python clean_prices.py           # Step 2: Price cleaning
python extract_colors.py         # Step 3: Color extraction
python import_to_database.py     # Step 4: Database import
```

## Project Structure

```
WebScraping/
├── api.py                          # FastAPI backend server
├── scraper_categories.py           # Web scraper for product data
├── clean_prices.py                 # Price normalization
├── extract_colors.py               # AI color extraction
├── import_to_database.py           # Database import logic
├── run_scraping_pipeline.py        # Automated pipeline orchestrator
├── fashion_scraper.db              # SQLite database
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── .dockerignore                   # Docker build exclusions
└── FE/                             # React frontend
    ├── src/
    │   ├── pages/                  # Page components
    │   │   ├── Home.tsx
    │   │   ├── WebScraping.tsx
    │   │   ├── Analytics.tsx
    │   │   └── ColorTrends.tsx
    │   ├── components/             # Reusable components
    │   │   └── ScrapingProgressModal.tsx
    │   └── services/
    │       └── api.ts              # API client
    └── package.json
```

## API Endpoints

### Products
- `GET /api/products` - Get paginated product list with filters
- `GET /api/filter-options` - Get available filter options
- `GET /api/price-history/{product_id}` - Get price history for a product

### Analytics
- `GET /api/stats` - Get database statistics
- `GET /api/price-trends` - Get price trends over time
- `GET /api/color-trends` - Get color distribution data
- `GET /api/product-timeline` - Get product launch timeline
- `GET /api/color-price-trends` - Get color vs price evolution

### Scraping
- `POST /api/run-scraping` - Trigger scraping pipeline (Server-Sent Events stream)

### Health
- `GET /health` - API health check

## Database Schema

### Main Tables

- `products` - Product information (id, name, url, site, gender, clothing_type, is_active)
- `prices` - Price history (product_id, price, date_scraped)
- `colors` - Color associations (product_id, color, date_extracted)
- `image_history` - Product image URLs (product_id, image_url, date_captured)
- `scraping_sessions` - Scraping session metadata (start_time, end_time, products_scraped)

## Technology Stack

### Backend
- Python 3.11
- FastAPI - Web framework
- Playwright/Patchright - Web scraping
- Pandas - Data processing
- SQLite - Database
- Uvicorn - ASGI server

### Frontend
- React 18
- TypeScript
- Vite - Build tool
- Recharts - Data visualization
- shadcn/ui - UI components
- Tailwind CSS - Styling

### DevOps
- Docker - Containerization
- Multi-stage builds - Optimized image size

## Troubleshooting

### Docker Build Issues

**Problem**: Build fails during frontend compilation
```bash
# Clear Docker cache and rebuild
docker build --no-cache -t fashion-scraper .
```

**Problem**: Port 8000 already in use
```bash
# Use a different port
docker run -p 8080:8000 fashion-scraper
# Access at http://localhost:8080
```

**Problem**: Container exits immediately
```bash
# Check container logs
docker logs <container_id>
```

### Scraping Issues

**Problem**: Scraper fails to load pages
- Check internet connection
- Verify target websites are accessible
- Playwright browsers may need reinstallation:
  ```bash
  playwright install chromium
  ```

**Problem**: No console output during scraping
- Ensure `PYTHONUNBUFFERED=1` is set
- Check that scripts have proper UTF-8 encoding
- On Windows, encoding issues may occur with special characters

**Problem**: Scraping takes too long
- This is normal - full scraping can take 10-15 minutes
- Monitor progress in the modal popup
- Each site requires multiple page loads and image processing

### Database Issues

**Problem**: Database locked error
- Close any other connections to fashion_scraper.db
- Restart the application
- Only one scraping session can run at a time

**Problem**: Missing data after scraping
- Check scraping logs for errors
- Verify import_to_database.py completed successfully
- Check that all 4 pipeline steps completed

### Frontend Issues

**Problem**: Charts not loading
- Check browser console for errors
- Verify API is running and accessible
- Ensure database has data to display

**Problem**: Filters not working
- Clear browser cache
- Check network tab for failed API requests
- Verify backend is returning filtered data

## Environment Variables

Optional environment variables for configuration:

- `VITE_API_URL` - Frontend API URL (default: http://localhost:8000)
- `PYTHONUNBUFFERED` - Enable unbuffered Python output (set to 1)
- `PYTHONIOENCODING` - Set Python encoding (set to utf-8)

## Advanced Docker Usage

### Persistent Database with Volume

To keep database changes between container restarts:

```bash
# Create a directory for data
mkdir data
cp fashion_scraper.db data/

# Run with volume mount
docker run -p 8000:8000 -v "$(pwd)/data:/app/data" fashion-scraper
```

Note: On Windows PowerShell, use `${PWD}` instead of `$(pwd)`

### Docker Compose (Optional)

Create a `docker-compose.yml` for easier management:

```yaml
version: '3.8'
services:
  fashion-scraper:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
      - PYTHONIOENCODING=utf-8
```

Then run:
```bash
docker-compose up
```

## Important Notes

- **Data Privacy**: Scraped data is stored locally in SQLite
- **Rate Limiting**: Built-in delays prevent server overload
- **Legal Compliance**: For competitive intelligence purposes only
- **Website Changes**: Selectors may need updates if sites change structure
- **Resource Usage**: Scraping requires ~2GB RAM for browser automation

## License

All rights reserved. For internal competitive intelligence use only.

---

**Version:** 2.0
**Last Updated:** October 2025
**Stack:** Python 3.11, FastAPI, React 18, TypeScript, Docker
