"""
Unified scraping pipeline that runs all steps in order:
1. Scrape data from websites
2. Clean prices
3. Extract colors
4. Import to database
"""

import subprocess
import sys
import io
import os
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


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
        print(log_message, flush=True)  # Force flush for real-time output

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
        self.log(description, "=" * 60, "info")
        self.log(description, f"▶ STARTING: {description}", "info")
        self.log(description, f"Script: {script_name}", "info")
        self.log(description, "=" * 60, "info")

        try:
            # Set environment for unbuffered output
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            env['PYTHONIOENCODING'] = 'utf-8'

            # Run the script and capture output
            process = subprocess.Popen(
                [sys.executable, '-u', script_name],  # -u for unbuffered
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env,
                encoding='utf-8',
                errors='replace'
            )

            line_count = 0
            # Stream output line by line - show EVERYTHING
            for line in process.stdout:
                line_stripped = line.rstrip('\n\r')  # Keep spacing but remove newlines
                # Show ALL output, even empty lines
                line_count += 1
                output_line = f"  {line_stripped}" if line_stripped else ""
                print(output_line, flush=True)
                if self.progress_callback:
                    self.progress_callback(description, output_line, "progress")

            # Wait for process to complete
            process.wait()

            if process.returncode == 0:
                self.log(description, "-" * 60, "success")
                self.log(description, f"✓ COMPLETED: {description}", "success")
                self.log(description, f"Output lines: {line_count}", "success")
                self.log(description, "-" * 60, "success")
                print(flush=True)  # Empty line for spacing
                return True
            else:
                self.log(description, "=" * 60, "error")
                self.log(description, f"✗ FAILED: {description}", "error")
                self.log(description, f"Exit code: {process.returncode}", "error")
                self.log(description, "=" * 60, "error")
                return False

        except Exception as e:
            self.log(description, "=" * 60, "error")
            self.log(description, f"✗ ERROR: {description}", "error")
            self.log(description, f"Exception: {str(e)}", "error")
            self.log(description, "=" * 60, "error")
            return False

    def run(self):
        """Run the complete scraping pipeline."""
        print(flush=True)
        print("╔" + "═" * 78 + "╗", flush=True)
        print("║" + " " * 20 + "FASHION SCRAPER PIPELINE" + " " * 34 + "║", flush=True)
        print("╚" + "═" * 78 + "╝", flush=True)
        print(flush=True)

        self.log("Pipeline", "🚀 Initializing scraping pipeline...", "info")
        print(flush=True)

        steps = [
            ("scraper_categories.py", "Step 1: Web Scraping", "Collecting product data from competitor websites"),
            ("clean_prices.py", "Step 2: Price Cleaning", "Normalizing and validating price information"),
            ("extract_colors.py", "Step 3: Color Extraction", "Analyzing and categorizing product colors"),
            ("import_to_database.py", "Step 4: Database Import", "Saving processed data to database"),
        ]

        total_steps = len(steps)

        for idx, (script, description, detail) in enumerate(steps, 1):
            self.log("Pipeline", f"📋 Progress: Step {idx}/{total_steps}", "info")
            self.log("Pipeline", f"📝 {detail}", "info")
            print(flush=True)

            success = self.run_script(script, description)

            if not success:
                print(flush=True)
                print("╔" + "═" * 78 + "╗", flush=True)
                print("║" + " " * 25 + "PIPELINE FAILED" + " " * 38 + "║", flush=True)
                print("╚" + "═" * 78 + "╝", flush=True)
                self.log("Pipeline", f"❌ Pipeline failed at: {description}", "error")
                return False

            print(flush=True)

        print(flush=True)
        print("╔" + "═" * 78 + "╗", flush=True)
        print("║" + " " * 22 + "PIPELINE COMPLETED" + " " * 37 + "║", flush=True)
        print("╚" + "═" * 78 + "╝", flush=True)
        print(flush=True)
        self.log("Pipeline", "✅ All steps completed successfully!", "success")
        self.log("Pipeline", f"📊 Total steps executed: {total_steps}", "success")
        self.log("Pipeline", "🎉 Data is ready for analysis!", "success")
        print(flush=True)
        return True


def main():
    """Main entry point for command-line usage."""
    pipeline = ScrapingPipeline()
    success = pipeline.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
