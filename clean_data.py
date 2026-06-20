"""
clean_data.py
-------------
Automated data cleaning module.

Reads the raw sales export and produces an analysis-ready dataset by:
  1. Removing exact duplicate records
  2. Standardizing text fields (casing, stray whitespace, category labels)
  3. Parsing multiple date formats into a single ISO format
  4. Cleaning numeric fields (currency symbols, thousands separators, invalid values)
  5. Handling missing values with column-appropriate strategies
  6. Logging every action taken so the cleaning process is auditable

Usage:
    python scripts/clean_data.py
"""

import pandas as pd
import numpy as np
import json
import os

RAW_PATH = "data/raw_sales_data.csv"
CLEAN_PATH = "output/cleaned_sales_data.csv"
LOG_PATH = "output/cleaning_log.json"

VALID_CATEGORIES = ["Electronics", "Apparel", "Home & Kitchen", "Stationery", "Beauty"]
VALID_REGIONS = ["North", "South", "East", "West"]
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"]


def parse_mixed_date(value):
    """Try a list of known formats; return ISO date string or NaT."""
    if pd.isna(value) or str(value).strip() == "":
        return pd.NaT
    value = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return pd.to_datetime(value, format=fmt)
        except ValueError:
            continue
    return pd.to_datetime(value, errors="coerce")  # last-resort fuzzy parse


def clean_price(value):
    """Strip currency symbols/commas and coerce to float."""
    if pd.isna(value) or str(value).strip() == "":
        return np.nan
    cleaned = (
        str(value)
        .replace("₹", "")
        .replace(",", "")
        .replace("Rs.", "")
        .replace("Rs", "")
        .strip()
    )
    try:
        return float(cleaned)
    except ValueError:
        return np.nan


def normalize_category(value):
    if pd.isna(value):
        return value
    value = str(value).strip().lower()
    for valid in VALID_CATEGORIES:
        if value == valid.lower():
            return valid
    return value.title()


def normalize_region(value):
    if pd.isna(value):
        return value
    value = str(value).strip().title()
    return value if value in VALID_REGIONS else value


def normalize_name(value):
    if pd.isna(value):
        return value
    return str(value).strip().title()


def run_cleaning():
    log = {"steps": []}

    df = pd.read_csv(RAW_PATH)
    rows_before = len(df)
    log["rows_before"] = rows_before
    log["missing_before"] = int(df.isna().sum().sum()) + int((df.astype(str).apply(
        lambda col: col.str.strip() == "")).sum().sum())

    # 1. Remove exact duplicate rows
    dup_count = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    log["steps"].append({
        "step": "remove_duplicates",
        "duplicates_removed": dup_count
    })

    # Treat blank strings as real missing values up front
    df = df.replace(r"^\s*$", np.nan, regex=True)

    # 2. Standardize text fields
    df["CustomerName"] = df["CustomerName"].apply(normalize_name)
    df["Category"] = df["Category"].apply(normalize_category)
    df["Region"] = df["Region"].apply(normalize_region)
    df["Product"] = df["Product"].astype(str).str.strip()
    df["PaymentMethod"] = df["PaymentMethod"].astype(str).str.strip()
    df["PaymentMethod"] = df["PaymentMethod"].replace("nan", np.nan)
    log["steps"].append({
        "step": "standardize_text",
        "columns": ["CustomerName", "Category", "Region", "Product", "PaymentMethod"],
        "detail": "Trimmed whitespace and normalized casing for consistent category/region labels"
    })

    # 3. Parse dates into a single ISO format
    df["OrderDate"] = df["OrderDate"].apply(parse_mixed_date)
    unparseable_dates = int(df["OrderDate"].isna().sum())
    log["steps"].append({
        "step": "standardize_dates",
        "formats_handled": DATE_FORMATS,
        "unparseable_dates": unparseable_dates
    })

    # 4. Clean numeric fields
    df["UnitPrice"] = df["UnitPrice"].apply(clean_price)
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    invalid_qty = int((df["Quantity"] <= 0).sum())
    df.loc[df["Quantity"] <= 0, "Quantity"] = np.nan
    log["steps"].append({
        "step": "clean_numeric_fields",
        "currency_symbols_stripped": True,
        "invalid_quantities_flagged": invalid_qty
    })

    # 5. Handle missing values with column-appropriate strategies
    missing_summary = {}

    # Critical identifier fields: drop rows missing OrderID or Product
    before_drop = len(df)
    df = df.dropna(subset=["OrderID", "Product"]).reset_index(drop=True)
    missing_summary["rows_dropped_missing_identifiers"] = before_drop - len(df)

    # Numeric fields: impute with the median for that product category
    for col in ["UnitPrice", "Quantity"]:
        na_count = int(df[col].isna().sum())
        df[col] = df.groupby("Category")[col].transform(lambda s: s.fillna(s.median()))
        df[col] = df[col].fillna(df[col].median())  # fallback for any category with all-NaN
        missing_summary[f"{col}_imputed_with_category_median"] = na_count

    # Categorical fields: impute with "Unknown" rather than dropping rows
    for col in ["CustomerName", "Region", "PaymentMethod"]:
        na_count = int(df[col].isna().sum())
        df[col] = df[col].fillna("Unknown")
        missing_summary[f"{col}_filled_unknown"] = na_count

    # Dates: drop rows where the date genuinely could not be parsed
    before_drop = len(df)
    df = df.dropna(subset=["OrderDate"]).reset_index(drop=True)
    missing_summary["rows_dropped_unparseable_date"] = before_drop - len(df)

    log["steps"].append({"step": "handle_missing_values", "detail": missing_summary})

    # Derived column used by the report generator
    df["Revenue"] = (df["UnitPrice"] * df["Quantity"]).round(2)
    df["OrderDate"] = df["OrderDate"].dt.strftime("%Y-%m-%d")

    rows_after = len(df)
    log["rows_after"] = rows_after
    log["missing_after"] = int(df.isna().sum().sum())
    log["rows_removed_total"] = rows_before - rows_after

    os.makedirs("output", exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

    print(f"Cleaned data saved to {CLEAN_PATH}")
    print(f"Cleaning log saved to {LOG_PATH}")
    print(f"Rows: {rows_before} -> {rows_after} | Duplicates removed: {dup_count} | "
          f"Missing values before: {log['missing_before']} -> after: {log['missing_after']}")

    return df, log


if __name__ == "__main__":
    run_cleaning()
