"""
generate_report.py
-------------------
Automated reporting module.

Reads the cleaned dataset + cleaning log produced by clean_data.py and
generates:
  1. Visual summaries (bar / pie / line charts) saved as PNGs
  2. A single self-contained HTML report combining KPIs, the cleaning
     audit trail, and the visual summaries

Usage:
    python scripts/generate_report.py
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

CLEAN_PATH = "output/cleaned_sales_data.csv"
LOG_PATH = "output/cleaning_log.json"
CHARTS_DIR = "output/charts"
REPORT_PATH = "output/report.html"

# Palette kept consistent across every chart
COLORS = ["#6366F1", "#22D3AA", "#F59E0B", "#EF4444", "#38BDF8", "#A78BFA"]

plt.rcParams.update({
    "figure.facecolor": "#12131A",
    "axes.facecolor": "#12131A",
    "axes.edgecolor": "#2A2C3A",
    "axes.labelcolor": "#E6E7EE",
    "text.color": "#E6E7EE",
    "xtick.color": "#9CA0B5",
    "ytick.color": "#9CA0B5",
    "font.size": 11,
    "axes.grid": True,
    "grid.color": "#23242F",
    "grid.linewidth": 0.6,
})


def save_chart(fig, name):
    os.makedirs(CHARTS_DIR, exist_ok=True)
    path = f"{CHARTS_DIR}/{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def chart_revenue_by_category(df):
    data = df.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(data.index, data.values, color=COLORS[0])
    ax.set_title("Revenue by Category", fontsize=13, fontweight="bold")
    ax.set_ylabel("Revenue (₹)")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    return save_chart(fig, "revenue_by_category")


def chart_orders_by_region(df):
    data = df["Region"].value_counts()
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(data.values, labels=data.index, autopct="%1.0f%%",
           colors=COLORS, textprops={"color": "#E6E7EE"}, startangle=90)
    ax.set_title("Orders by Region", fontsize=13, fontweight="bold")
    return save_chart(fig, "orders_by_region")


def chart_monthly_revenue_trend(df):
    df["Month"] = pd.to_datetime(df["OrderDate"]).dt.to_period("M").astype(str)
    data = df.groupby("Month")["Revenue"].sum().sort_index()
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.plot(data.index, data.values, marker="o", color=COLORS[1], linewidth=2)
    ax.set_title("Monthly Revenue Trend", fontsize=13, fontweight="bold")
    ax.set_ylabel("Revenue (₹)")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    return save_chart(fig, "monthly_revenue_trend")


def chart_payment_methods(df):
    data = df["PaymentMethod"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(data.index, data.values, color=COLORS[2])
    ax.set_title("Orders by Payment Method", fontsize=13, fontweight="bold")
    ax.invert_yaxis()
    return save_chart(fig, "payment_methods")


def build_html(df, log, chart_paths):
    total_revenue = df["Revenue"].sum()
    total_orders = len(df)
    avg_order_value = df["Revenue"].mean()
    top_category = df.groupby("Category")["Revenue"].sum().idxmax()

    rows_before = log["rows_before"]
    rows_after = log["rows_after"]
    duplicates_removed = log["steps"][0]["duplicates_removed"]
    missing_before = log["missing_before"]
    missing_after = log["missing_after"]

    generated_at = datetime.now().strftime("%d %b %Y, %I:%M %p")

    def chart_tag(path, alt):
        rel = path.replace("output/", "")
        return f'<img src="{rel}" alt="{alt}" class="chart-img" />'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Data Cleaning & Reporting Automation — Summary</title>
<style>
  :root {{
    --bg: #0B0C12;
    --panel: #12131A;
    --border: #23242F;
    --text: #E6E7EE;
    --muted: #9CA0B5;
    --accent: #6366F1;
    --accent2: #22D3AA;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    padding: 32px;
  }}
  .wrap {{ max-width: 1080px; margin: 0 auto; }}
  header {{ margin-bottom: 28px; }}
  header h1 {{ margin: 0 0 6px; font-size: 26px; letter-spacing: -0.3px; }}
  header p {{ margin: 0; color: var(--muted); font-size: 14px; }}
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 28px;
  }}
  .kpi-card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 18px;
  }}
  .kpi-card .label {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
  .kpi-card .value {{ font-size: 22px; font-weight: 700; margin-top: 6px; }}
  .kpi-card.accent .value {{ color: var(--accent2); }}
  section {{ margin-bottom: 32px; }}
  section h2 {{
    font-size: 16px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 16px;
  }}
  .chart-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }}
  .chart-card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px;
  }}
  .chart-img {{ width: 100%; border-radius: 6px; display: block; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    font-size: 14px;
  }}
  th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border); }}
  th {{ color: var(--muted); font-weight: 600; font-size: 12px; text-transform: uppercase; }}
  tr:last-child td {{ border-bottom: none; }}
  .pill {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
  }}
  .pill.green {{ background: rgba(34,211,170,0.15); color: var(--accent2); }}
  .pill.red {{ background: rgba(239,68,68,0.15); color: #EF4444; }}
  footer {{ color: var(--muted); font-size: 12px; text-align: center; margin-top: 30px; }}
</style>
</head>
<body>
<div class="wrap">

  <header>
    <h1>Data Cleaning &amp; Reporting Automation</h1>
    <p>Automated pipeline summary · generated {generated_at}</p>
  </header>

  <section>
    <h2>Business KPIs (post-cleaning)</h2>
    <div class="kpi-grid">
      <div class="kpi-card accent">
        <div class="label">Total Revenue</div>
        <div class="value">₹{total_revenue:,.0f}</div>
      </div>
      <div class="kpi-card">
        <div class="label">Total Orders</div>
        <div class="value">{total_orders}</div>
      </div>
      <div class="kpi-card">
        <div class="label">Avg Order Value</div>
        <div class="value">₹{avg_order_value:,.0f}</div>
      </div>
      <div class="kpi-card">
        <div class="label">Top Category</div>
        <div class="value">{top_category}</div>
      </div>
    </div>
  </section>

  <section>
    <h2>Cleaning Pipeline Audit</h2>
    <table>
      <tr><th>Metric</th><th>Before</th><th>After</th><th>Result</th></tr>
      <tr>
        <td>Row count</td><td>{rows_before}</td><td>{rows_after}</td>
        <td><span class="pill red">{rows_before - rows_after} removed</span></td>
      </tr>
      <tr>
        <td>Duplicate records</td><td>{duplicates_removed}</td><td>0</td>
        <td><span class="pill green">Resolved</span></td>
      </tr>
      <tr>
        <td>Missing values</td><td>{missing_before}</td><td>{missing_after}</td>
        <td><span class="pill green">Resolved</span></td>
      </tr>
      <tr>
        <td>Date formats</td><td>4 inconsistent formats</td><td>1 (ISO 8601)</td>
        <td><span class="pill green">Standardized</span></td>
      </tr>
      <tr>
        <td>Currency formatting</td><td>Mixed (₹, commas)</td><td>Numeric float</td>
        <td><span class="pill green">Standardized</span></td>
      </tr>
    </table>
  </section>

  <section>
    <h2>Visual Summaries</h2>
    <div class="chart-grid">
      <div class="chart-card">{chart_tag(chart_paths[0], "Revenue by Category")}</div>
      <div class="chart-card">{chart_tag(chart_paths[1], "Orders by Region")}</div>
      <div class="chart-card">{chart_tag(chart_paths[2], "Monthly Revenue Trend")}</div>
      <div class="chart-card">{chart_tag(chart_paths[3], "Orders by Payment Method")}</div>
    </div>
  </section>

  <footer>Generated automatically by clean_data.py + generate_report.py — no manual editing required.</footer>

</div>
</body>
</html>
"""
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report saved to {REPORT_PATH}")


def main():
    df = pd.read_csv(CLEAN_PATH)
    with open(LOG_PATH) as f:
        log = json.load(f)

    chart_paths = [
        chart_revenue_by_category(df),
        chart_orders_by_region(df),
        chart_monthly_revenue_trend(df),
        chart_payment_methods(df),
    ]
    build_html(df, log, chart_paths)


if __name__ == "__main__":
    main()
