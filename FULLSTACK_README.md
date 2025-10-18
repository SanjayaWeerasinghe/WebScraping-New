# Fashion Scraper Full Stack Application

Complete guide to running the Fashion Scraper with React frontend and FastAPI backend.

## Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌──────────────────┐
│  React Frontend │ ◄─────► │  FastAPI Backend │ ◄─────► │  SQLite Database │
│  (Port 5173)    │   HTTP  │  (Port 8000)     │         │  (fashion_scraper.db) │
└─────────────────┘         └─────────────────┘         └──────────────────┘
```

## Prerequisites

- Python 3.10+
- Node.js 18+ (or Bun)
- Git

## Quick Start

### 1. Backend Setup (Python)

```bash
# Install Python dependencies
py -m pip install -r requirements.txt

# Initialize database (if not already done)
py init_database.py

# Import existing data (if not already done)
py import_to_database.py

# Start API server
py api.py
```

The API will be available at: **http://localhost:8000**
API documentation at: **http://localhost:8000/docs**

### 2. Frontend Setup (React)

```bash
# Navigate to frontend directory
cd FE

# Install dependencies (using npm)
npm install

# Start development server
npm run dev
```

The frontend will be available at: **http://localhost:5173**

## API Endpoints

### GET `/api/products`
Fetch all products with filtering options.

**Query Parameters:**
- `site` - Filter by site (fashionbug/coolplanet)
- `gender` - Filter by gender (men/women)
- `clothing_type` - Filter by clothing type
- `limit` - Maximum results (default 1000)

**Example:**
```bash
curl "http://localhost:8000/api/products?site=fashionbug&limit=10"
```

### GET `/api/price-history/{product_id}`
Get price history for a specific product.

**Example:**
```bash
curl "http://localhost:8000/api/price-history/1"
```

### GET `/api/color-trends`
Get color distribution across products.

**Query Parameters:**
- `site` - Optional site filter

**Example:**
```bash
curl "http://localhost:8000/api/color-trends?site=coolplanet"
```

### GET `/api/stats`
Get database statistics.

**Example:**
```bash
curl "http://localhost:8000/api/stats"
```

## Frontend Pages

### Home (`/`)
Dashboard overview with statistics

### Price Analysis (`/price-analysis`)
- Price vs Clothing Type scatter plots
- Price vs Clothing Subtype comparison
- Competitor price comparison charts
- Real-time filtering by site, gender, and clothing type

### Color Trends (`/color-trends`)
Color distribution analysis across products

### Web Scraping (`/scraping`)
Manage scraping sessions and view scraping history

## Complete Workflow

### 1. Initial Setup (One Time)

```bash
# Backend
py -m pip install -r requirements.txt
py init_database.py

# Scrape data
py scraper_categories.py
py clean_prices.py
py extract_colors.py
py import_to_database.py

# Frontend
cd FE
npm install
cd ..
```

### 2. Running the Application

**Terminal 1 - Backend:**
```bash
py api.py
```

**Terminal 2 - Frontend:**
```bash
cd FE
npm run dev
```

**Access the application:**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

### 3. Regular Scraping Updates

When you want to scrape new data:

```bash
# 1. Scrape new data
py scraper_categories.py

# 2. Clean prices
py clean_prices.py

# 3. Extract colors
py extract_colors.py

# 4. Import to database (with notes)
py import_to_database.py
# Enter notes like: "Weekly scrape - Oct 25, 2025"

# 5. Refresh frontend to see new data
```

The frontend will automatically fetch the updated data!

## Environment Variables

### Backend (.env)
Create a `.env` file in the root directory:

```env
# Database path (optional, defaults to ./fashion_scraper.db)
DATABASE_PATH=fashion_scraper.db

# API port (optional, defaults to 8000)
PORT=8000
```

### Frontend (FE/.env)
Create a `.env` file in the `FE` directory:

```env
# API URL
VITE_API_URL=http://localhost:8000
```

## Development Tips

### Backend Development

**Hot reload with uvicorn:**
```bash
py -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**View API documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Development

**Build for production:**
```bash
cd FE
npm run build
```

**Preview production build:**
```bash
npm run preview
```

**Type checking:**
```bash
npm run lint
```

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
py -m pip install fastapi uvicorn pydantic
```

**Problem:** Database not found
```bash
# Make sure you've initialized the database
py init_database.py
py import_to_database.py
```

**Problem:** CORS errors
- Check that the frontend URL is in `api.py` CORS origins
- Default: `http://localhost:5173`

### Frontend Issues

**Problem:** `Failed to fetch products`
- Ensure backend is running on port 8000
- Check `VITE_API_URL` in `FE/.env`
- Visit http://localhost:8000 to verify API is up

**Problem:** No data showing
- Check browser console for errors
- Verify database has data: `py verify_database.py`
- Check API response: http://localhost:8000/api/products

**Problem:** Module not found errors
```bash
cd FE
rm -rf node_modules package-lock.json
npm install
```

## Production Deployment

### Backend (FastAPI)

**Using Gunicorn:**
```bash
pip install gunicorn
gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (React)

**Build and serve:**
```bash
cd FE
npm run build
# Serve the 'dist' directory with any static file server
```

## Database Management

### Backup Database
```bash
copy fashion_scraper.db backups\fashion_scraper_%date%.db
```

### Query Database Directly
```bash
py query_database.py
```

### View Sample Records
```bash
py verify_database.py
```

## Tech Stack

### Backend
- FastAPI - Modern Python web framework
- SQLite - Lightweight database
- Pydantic - Data validation
- Uvicorn - ASGI server

### Frontend
- React 18 - UI library
- TypeScript - Type safety
- Vite - Build tool
- TanStack Query - Data fetching
- Recharts - Data visualization
- shadcn/ui - UI components
- Tailwind CSS - Styling

## Support

For issues:
1. Check this README
2. View API docs: http://localhost:8000/docs
3. Check database: `py verify_database.py`
4. Check logs in terminal

## License

MIT
