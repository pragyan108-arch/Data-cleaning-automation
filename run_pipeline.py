"""
run_pipeline.py
----------------
Single entry point for the full Data Cleaning & Reporting Automation
pipeline. Running this script will:

  1. Clean the raw dataset (data/raw_sales_data.csv)
  2. Generate visual summaries + an HTML report (output/report.html)

This is the script to run for a fresh end-to-end demonstration.
"""

from scripts.clean_data import run_cleaning
from scripts.generate_report import main as generate_report


def main():
    print("=" * 60)
    print("STEP 1/2: Cleaning raw data...")
    print("=" * 60)
    run_cleaning()

    print()
    print("=" * 60)
    print("STEP 2/2: Generating automated report...")
    print("=" * 60)
    generate_report()

    print()
    print("Pipeline complete. Open output/report.html in your browser to view the report.")


if __name__ == "__main__":
    main()
