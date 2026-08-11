"""
02_sql_load_run.py — Load clean data into SQLite and run the analysis queries.
Demonstrates the SQL half of the project (joins, CTEs, window functions).
Results are printed and saved to data/sql_results.json for the dashboard.
"""
import sqlite3, json
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"

def main():
    df = pd.read_parquet(DATA / "clean.parquet")
    con = sqlite3.connect(DATA / "retail.db")
    df.to_sql("retail", con, if_exists="replace", index=False)
    con.execute("CREATE INDEX IF NOT EXISTS ix_cust ON retail(CustomerID)")
    con.execute("CREATE INDEX IF NOT EXISTS ix_country ON retail(Country)")

    out = {}

    # Split the .sql file into individual statements and run the labelled ones.
    q = {}
    q["monthly_revenue"] = """
        WITH monthly AS (
            SELECT InvoiceYearMonth ym, ROUND(SUM(Revenue),2) revenue,
                   COUNT(DISTINCT InvoiceNo) orders,
                   COUNT(DISTINCT CustomerID) active_customers
            FROM retail GROUP BY InvoiceYearMonth)
        SELECT ym, revenue, orders, active_customers,
               ROUND(100.0*(revenue-LAG(revenue) OVER (ORDER BY ym))
                     /LAG(revenue) OVER (ORDER BY ym),1) mom_growth_pct
        FROM monthly ORDER BY ym;"""

    q["top_countries"] = """
        SELECT Country, ROUND(SUM(Revenue),2) revenue,
               COUNT(DISTINCT CustomerID) customers,
               ROUND(100.0*SUM(Revenue)/(SELECT SUM(Revenue) FROM retail),1) pct_of_total
        FROM retail GROUP BY Country ORDER BY revenue DESC LIMIT 10;"""

    q["top_products"] = """
        SELECT StockCode, MAX(Description) description, SUM(Quantity) units_sold,
               ROUND(SUM(Revenue),2) revenue
        FROM retail GROUP BY StockCode ORDER BY revenue DESC LIMIT 10;"""

    q["pareto_quintiles"] = """
        WITH cust AS (SELECT CustomerID, SUM(Revenue) spend FROM retail GROUP BY CustomerID),
        ranked AS (SELECT CustomerID, spend, NTILE(5) OVER (ORDER BY spend DESC) quintile FROM cust)
        SELECT quintile, COUNT(*) customers, ROUND(SUM(spend),2) revenue,
               ROUND(100.0*SUM(spend)/(SELECT SUM(spend) FROM cust),1) pct_of_revenue
        FROM ranked GROUP BY quintile ORDER BY quintile;"""

    q["repeat_rate"] = """
        WITH opc AS (SELECT CustomerID, COUNT(DISTINCT InvoiceNo) n FROM retail GROUP BY CustomerID)
        SELECT COUNT(*) total_customers,
               SUM(CASE WHEN n>1 THEN 1 ELSE 0 END) repeat_customers,
               ROUND(100.0*SUM(CASE WHEN n>1 THEN 1 ELSE 0 END)/COUNT(*),1) repeat_rate_pct,
               ROUND(AVG(n),2) avg_orders_per_customer
        FROM opc;"""

    q["aov"] = "SELECT ROUND(SUM(Revenue)/COUNT(DISTINCT InvoiceNo),2) avg_order_value FROM retail;"

    for name, sql in q.items():
        out[name] = pd.read_sql_query(sql, con).to_dict(orient="records")

    con.close()
    with open(DATA / "sql_results.json", "w") as f:
        json.dump(out, f, indent=2)

    print("Monthly revenue (head):")
    for r in out["monthly_revenue"]:
        print(f"  {r['ym']}  £{r['revenue']:>12,.0f}  MoM {r['mom_growth_pct']}%")
    print("\nTop 5 countries:")
    for r in out["top_countries"][:5]:
        print(f"  {r['Country']:<16} £{r['revenue']:>12,.0f}  ({r['pct_of_total']}%)")
    print("\nPareto:", out["pareto_quintiles"])
    print("Repeat:", out["repeat_rate"])
    print("AOV:", out["aov"])

if __name__ == "__main__":
    main()
