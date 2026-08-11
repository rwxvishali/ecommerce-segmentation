"""
01_clean.py — Load and clean the UCI Online Retail dataset.

Business context: A UK-based online gift retailer. Raw transactional data is
messy — it contains cancellations, returns, missing customer IDs, and
non-product line items (postage, bank charges, manual adjustments). Before any
customer analysis we need one clean, trustworthy table of real purchases.
"""
import pandas as pd
import numpy as np
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
RAW = DATA / "online_retail.csv"

def main():
    df = pd.read_csv(RAW, encoding="ISO-8859-1")
    audit = {"0_raw_rows": int(len(df))}

    # --- Parse types ---
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["CustomerID"] = df["CustomerID"]  # keep float w/ NaN for now

    # --- Data-quality filters (each logged so the cleaning is auditable) ---
    # 1. Drop rows with no CustomerID: cannot attribute to a customer -> useless for segmentation
    before = len(df); df = df[df["CustomerID"].notna()]
    audit["1_dropped_no_customer"] = int(before - len(df))

    # 2. Drop cancellations: InvoiceNo starting with 'C' are cancelled orders
    before = len(df)
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    audit["2_dropped_cancellations"] = int(before - len(df))

    # 3. Drop non-positive quantity (returns/adjustments) and non-positive price
    before = len(df)
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    audit["3_dropped_nonpositive_qty_price"] = int(before - len(df))

    # 4. Drop non-product stock codes (postage, bank charges, manuals, samples, etc.)
    non_products = {"POST", "DOT", "M", "D", "CRUK", "PADS", "BANK CHARGES",
                    "AMAZONFEE", "S", "C2", "gift_0001"}
    before = len(df)
    sc = df["StockCode"].astype(str).str.upper().str.strip()
    df = df[~sc.isin({c.upper() for c in non_products})]
    # also drop pure test/adjust codes that are all letters (e.g. 'B', 'BANK...')
    df = df[~sc.str.fullmatch(r"[A-Z]+")]
    audit["4_dropped_non_product_codes"] = int(before - len(df))

    # 5. Drop exact duplicate transaction lines
    before = len(df)
    df = df.drop_duplicates()
    audit["5_dropped_duplicates"] = int(before - len(df))

    # --- Derived fields ---
    df["CustomerID"] = df["CustomerID"].astype(int)
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["InvoiceYearMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["InvoiceDay"] = df["InvoiceDate"].dt.date.astype(str)

    audit["6_final_rows"] = int(len(df))
    audit["retained_pct"] = round(100 * len(df) / audit["0_raw_rows"], 1)
    audit["final_customers"] = int(df["CustomerID"].nunique())
    audit["final_orders"] = int(df["InvoiceNo"].nunique())
    audit["final_products"] = int(df["StockCode"].nunique())
    audit["final_countries"] = int(df["Country"].nunique())
    audit["total_revenue"] = round(float(df["Revenue"].sum()), 2)
    audit["date_min"] = str(df["InvoiceDate"].min().date())
    audit["date_max"] = str(df["InvoiceDate"].max().date())

    df.to_parquet(DATA / "clean.parquet", index=False)
    df.to_csv(DATA / "clean.csv", index=False)
    with open(DATA / "cleaning_audit.json", "w") as f:
        json.dump(audit, f, indent=2)

    print("=== CLEANING AUDIT ===")
    for k, v in audit.items():
        print(f"{k:35s} {v}")

if __name__ == "__main__":
    main()
