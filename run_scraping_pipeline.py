"""
Unified scraping pipeline that runs all steps in order:
1. Scrape data from websites
2. Clean prices
3. Extract colors
4. Import to database
"""

import subprocess
import sys
from datetime import datetime


class ScrapingPipeline:
    def __init__(self, progress_callback=None):
        """
        Initialize the scraping pipeline.

        Args:
            progress_callback: Optional callback function to report progress
                              Should accept (step, message, status) parameters
        """
        self.progress_callback = progress_callback

    def log(self, step, message, status="info"):
        """Log progress and call callback if provided."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{status.upper()}] {step}: {message}"
        print(log_message)

        if self.progress_callback:
            self.progress_callback(step, message, status)

    def run_script(self, script_name, description):
        """
        Run a Python script and capture its output.

        Args:
            script_name: Name of the Python script to run
            description: Human-readable description of the step

        Returns:
            bool: True if successful, False otherwise
        """
        self.log(description, f"Starting {script_name}...", "info")

        try:
            # Run the script and capture output
            process = subprocess.Popen(
                [sys.executable, script_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Stream output line by line
            for line in process.stdout:
                line = line.strip()
                if line:
                    print(line)
                    if self.progress_callback:
                        self.progress_callback(description, line, "progress")

            # Wait for process to complete
            process.wait()

            if process.returncode == 0:
                self.log(description, f"✓ Completed {script_name}", "success")
                return True
            else:
                self.log(description, f"✗ Failed with exit code {process.returncode}", "error")
                return False

        except Exception as e:
            self.log(description, f"✗ Error: {str(e)}", "error")
            return False

    def run(self):
        """Run the complete scraping pipeline."""
        self.log("Pipeline", "Starting scraping pipeline", "info")

        steps = [
            ("scraper_categories.py", "Step 1: Web Scraping"),
            ("clean_prices.py", "Step 2: Price Cleaning"),
            ("extract_colors.py", "Step 3: Color Extraction"),
            ("import_to_database.py", "Step 4: Database Import"),
        ]

        for script, description in steps:
            success = self.run_script(script, description)
            if not success:
                self.log("Pipeline", f"Pipeline failed at: {description}", "error")
                return False

        self.log("Pipeline", "✓ Pipeline completed successfully!", "success")
        return True


def main():
    """Main entry point for command-line usage."""
    pipeline = ScrapingPipeline()
    success = pipeline.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
