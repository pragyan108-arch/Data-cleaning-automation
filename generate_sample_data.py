"""
generate_sample_data.py
------------------------
Creates a realistic, intentionally messy e-commerce sales dataset so the
cleaning pipeline has real problems to solve: missing values, duplicate
rows, inconsistent text casing/spacing, mixed date formats, and invalid
numeric entries.

Run once to (re)create data/raw_sales_data.csv. Safe to re-run; uses a
fixed random seed so output is reproducible.
"""

import random
import csv
from datetime import datetime, timedelta

random.seed(42)

PRODUCTS = {
    "Electronics": ["Wireless Mouse", "Bluetooth Speaker", "USB-C Cable", "Laptop Stand", "Webcam HD"],
    "Apparel": ["Cotton T-Shirt", "Denim Jacket", "Running Shoes", "Wool Sweater", "Sports Cap"],
    "Home & Kitchen": ["Non-Stick Pan", "LED Desk Lamp", "Coffee Mug Set", "Storage Box", "Wall Clock"],
    "Stationery": ["Notebook Pack", "Gel Pen Set", "Sticky Notes", "Desk Organizer", "Highlighter Pack"],
    "Beauty": ["Face Wash", "Hair Serum", "Lip Balm", "Sunscreen SPF50", "Body Lotion"],
}

REGIONS = ["North", "South", "East", "West"]
PAYMENT_METHODS = ["Credit Card", "UPI", "Debit Card", "Net Banking", "Cash on Delivery"]
FIRST_NAMES = ["Aman", "Priya", "Rohan", "Sneha", "Vikram", "Anjali", "Karan", "Pooja", "Rahul", "Isha",
               "Dev", "Neha", "Arjun", "Simran", "Aditya", "Riya"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Kumar", "Singh", "Mehta", "Reddy", "Joshi", "Patel", "Nair"]

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"]


def messy_text(text, mode):
    """Apply random casing/whitespace inconsistencies to a string."""
    if mode == 0:
        return text.upper()
    if mode == 1:
        return text.lower()
    if mode == 2:
        return f"  {text}  "  # stray whitespace
    return text  # clean


def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def build_rows(n=320):
    rows = []
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 6, 1)

    for i in range(1, n + 1):
        category = random.choice(list(PRODUCTS.keys()))
        product = random.choice(PRODUCTS[category])
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        qty = random.choice([1, 1, 2, 2, 3, 4, 5, -1])  # occasional invalid negative qty
        unit_price = round(random.uniform(150, 4500), 2)
        region = random.choice(REGIONS)
        payment = random.choice(PAYMENT_METHODS)
        order_date = random_date(start_date, end_date)
        date_fmt = random.choice(DATE_FORMATS)
        date_str = order_date.strftime(date_fmt)

        row = {
            "OrderID": f"ORD{1000 + i}",
            "CustomerName": messy_text(name, random.choice([0, 1, 2, 3])),
            "Product": product,
            "Category": messy_text(category, random.choice([0, 1, 2, 3])),
            "Quantity": qty,
            "UnitPrice": unit_price,
            "OrderDate": date_str,
            "Region": messy_text(region, random.choice([0, 3, 3])),
            "PaymentMethod": payment,
        }
        rows.append(row)

    # Inject missing values randomly across a handful of columns
    missing_targets = random.sample(range(len(rows)), k=int(n * 0.10))
    for idx in missing_targets:
        field = random.choice(["CustomerName", "UnitPrice", "Region", "PaymentMethod", "Quantity"])
        rows[idx][field] = ""

    # Inject exact duplicate rows
    dup_sample = random.sample(rows, k=int(n * 0.06))
    rows.extend([r.copy() for r in dup_sample])

    # Inject a few rows with malformed price strings (currency symbols, commas)
    malformed_idx = random.sample(range(len(rows)), k=8)
    for idx in malformed_idx:
        price = rows[idx]["UnitPrice"]
        if price != "":
            rows[idx]["UnitPrice"] = f"₹{price:,.2f}"

    random.shuffle(rows)
    return rows


def main():
    rows = build_rows()
    fieldnames = ["OrderID", "CustomerName", "Product", "Category", "Quantity",
                  "UnitPrice", "OrderDate", "Region", "PaymentMethod"]

    out_path = "data/raw_sales_data.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows -> {out_path}")


if __name__ == "__main__":
    main()
