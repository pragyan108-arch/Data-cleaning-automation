# Data Cleaning & Reporting Automation

Automated Python pipeline that takes a messy, real-world-style sales export and turns it into an analysis-ready dataset plus a visual HTML report — with zero manual spreadsheet editing.

## Problem It Solves

Raw business data is rarely clean. This project simulates a typical e-commerce sales export with the kinds of issues analysts run into every day, and automates the fix:

| Issue in raw data | How the pipeline handles it |
|---|---|
| Duplicate order records | Detected and removed automatically |
| Missing values (price, region, payment method, etc.) | Imputed with category-level medians (numeric) or `"Unknown"` (categorical), with every fill logged |
| Inconsistent text casing (`ELECTRONICS`, `electronics`, `  Electronics  `) | Standardized to a single consistent label per field |
| Mixed date formats (`YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`, `DD-MM-YYYY`) | Parsed and normalized to ISO 8601 (`YYYY-MM-DD`) |
| Inconsistent currency formatting (`₹2,149.54` vs `2149.54`) | Stripped and converted to clean numeric floats |
| Invalid values (negative quantities) | Flagged as missing, then imputed rather than silently kept |

## Key Features

- **End-to-end automation** — one command takes raw CSV → cleaned CSV → full HTML report
- **Auditable cleaning** — every transformation (duplicates removed, values imputed, formats fixed) is logged to `output/cleaning_log.json` so nothing happens silently
- **Automated visual summaries** — revenue by category, orders by region, monthly revenue trend, and orders by payment method, generated fresh on every run
- **Self-contained HTML report** — KPI cards, a before/after cleaning audit table, and all charts in a single dark-themed `report.html` that opens in any browser

## Tech Stack

Python · pandas · NumPy · Matplotlib

## Folder Structure

```
data-cleaning-automation/
├── data/
│   └── raw_sales_data.csv          # Sample messy input dataset
├── scripts/
│   ├── generate_sample_data.py     # Recreates the messy sample dataset
│   ├── clean_data.py               # Cleaning pipeline
│   └── generate_report.py          # Chart + HTML report generation
├── output/
│   ├── cleaned_sales_data.csv      # Cleaned, analysis-ready data
│   ├── cleaning_log.json           # Audit trail of every cleaning action
│   ├── report.html                 # Final visual report
│   └── charts/                     # PNG charts embedded in the report
├── run_pipeline.py                 # Single entry point: cleaning + reporting
├── requirements.txt
└── README.md
```

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the full pipeline
python run_pipeline.py

# 3. Open the report
open output/report.html        # macOS
start output/report.html       # Windows
```

To generate a fresh messy dataset (optional — one is already included):

```bash
python scripts/generate_sample_data.py
```

## What the Report Shows

- **Business KPIs**: total revenue, total orders, average order value, top category
- **Cleaning Pipeline Audit**: row counts and missing-value counts before/after, duplicates resolved, date and currency formats standardized
- **Visual Summaries**: four charts covering category revenue, regional order distribution, the monthly revenue trend, and payment method breakdown

## Expected Outcome

This project demonstrates a practical, end-to-end understanding of:

- Data preprocessing (handling missing values, duplicates, and inconsistent formatting)
- Building repeatable automation rather than one-off manual cleaning
- Turning a cleaned dataset into a decision-ready visual report

## Author

Pragyan Sharma
