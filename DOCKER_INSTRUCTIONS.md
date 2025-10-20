# Fashion Scraper - Docker Setup

This application is containerized using Docker for easy deployment.

## Prerequisites

- Docker Desktop installed on your machine
- At least 3GB of free disk space

## How to Run

### Option 1: Build and Run (Recommended)

1. Open a terminal in the project directory
2. Build the Docker image:
   ```bash
   docker build -t fashion-scraper .
   ```

   **Note:** This will take 5-10 minutes as it downloads:
   - Node.js and Python dependencies
   - Chromium browser (~400MB)
   - System libraries for browser automation

3. Run the container:
   ```bash
   docker run -d -p 8000:8000 --name fashion-scraper fashion-scraper
   ```

4. Open your browser and go to:
   - Application: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Quick Start (if you receive a Docker image file)

If you received a `.tar` file:

1. Load the image:
   ```bash
   docker load -i fashion-scraper.tar
   ```

2. Run the container:
   ```bash
   docker run -d -p 8000:8000 --name fashion-scraper fashion-scraper
   ```

## Useful Commands

### View logs
```bash
docker logs fashion-scraper
```

### View live logs (follow)
```bash
docker logs -f fashion-scraper
```

### Stop the container
```bash
docker stop fashion-scraper
```

### Start the container again
```bash
docker start fashion-scraper
```

### Remove the container
```bash
docker stop fashion-scraper
docker rm fashion-scraper
```

### Remove the image
```bash
docker rmi fashion-scraper
```

## Troubleshooting

### Port 8000 already in use
If you get an error that port 8000 is already in use, run on a different port:
```bash
docker run -d -p 8080:8000 --name fashion-scraper fashion-scraper
```
Then access the app at http://localhost:8080

### Container won't start
Check the logs to see what went wrong:
```bash
docker logs fashion-scraper
```

### Browser automation errors
The Chromium browser is included in the image. If you get browser-related errors, ensure you built the image completely (the build process should take several minutes).

## What's Inside

- **Frontend**: React + TypeScript + Vite
- **Backend**: Python + FastAPI
- **Browser Automation**: Playwright (with Chromium)
- **Database**: SQLite (fashion_scraper.db)

## Notes

- The image size is approximately 2.9GB due to the included Chromium browser
- First build takes longer; subsequent builds use Docker cache
- The application runs on port 8000 inside the container
- All data is stored in the included SQLite database
