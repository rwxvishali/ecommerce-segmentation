# Online Retail — Customer Segmentation & Analytics

**End-to-end analytics project: raw transactions → clean SQL warehouse → customer segmentation → a live, interviewer-ready dashboard.**

A UK-based online gift retailer has one year of messy transactional data and no idea *who* its best customers are. This project turns 541,909 raw rows into a clear answer — which customers drive the money, which are slipping away, and what to do about each group — and presents it in an interactive dashboard you can walk a stakeholder through.

**Stack:** Python (pandas, scikit-learn) · SQL (SQLite: CTEs, window functions) · self-contained HTML/SVG dashboard
**Dataset:** [UCI / Kaggle Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail) — 541,909 transactions, Dec 2010–Dec 2011.

---

## The business questions

1. Where does revenue actually come from — which customers, products, and markets?
2. How loyal is the customer base, and how concentrated is spend?
3. Can we segment customers into actionable groups, both with transparent rules *and* with unsupervised learning?
4. What specific actions should marketing take for each segment, and what is the upside?

## Headline results

| Metric | Value |
|---|---|
| Clean revenue analysed | **£8.74M** across 4,334 customers / 18,402 orders |
| Revenue concentration | **Top 20% of customers = 74.6% of revenue** |
| Repeat-purchase rate | **65.3%** (avg 4.25 orders per customer) |
| VIP cluster (KMeans) | **686 customers drive 64% of revenue** (avg 14 orders, £8,169 each) |
| Revenue "at risk" | **£510k** sitting in high-value customers who have gone quiet |

## What I did

**1. Data cleaning (auditable).** Removed cancellations, returns, missing customer IDs, non-product line items (postage, bank charges, adjustments), and duplicates — every filter logged to `data/cleaning_audit.json`. 72.2% of rows retained as trustworthy purchases.

**2. SQL analysis layer.** Loaded the clean data into SQLite and answered the business questions with real SQL — monthly revenue with month-over-month growth via `LAG()`, a Pareto quintile breakdown via `NTILE()`, repeat-rate, AOV, and top products/markets. See `sql/analysis.sql`.

**3. Customer segmentation — two complementary views.**
   - *Rule-based RFM:* Recency / Frequency / Monetary scored into quintiles and mapped to business-friendly segments (Champions, Loyal, At Risk, Hibernating, …). Transparent and easy to hand to marketing.
   - *Unsupervised KMeans:* clustering on standardized `log(RFM)`, with **k chosen by silhouette score** (k=4, silhouette 0.34). Confirms and sharpens the rule-based view.

**4. From analysis to action.** Each segment gets a costed recommendation — e.g. a win-back campaign on the At Risk group where recovering just 20% of the £510k is ≈ £102k/yr for the price of one email flow.

**5. Live dashboard.** A single self-contained `dashboard/index.html` (no server, no build) with KPIs, an interactive revenue trend, Pareto and market breakdowns, RFM segment bars, KMeans cluster facets, top products, and the findings/recommendations — light & dark mode, hover tooltips, and accessible table views. This is the piece you demo in an interview.

## How to run

```bash
pip install pandas numpy scikit-learn pyarrow openpyxl
python src/01_clean.py            # clean -> data/clean.parquet + audit
python src/02_sql_load_run.py     # SQLite load + analysis queries
python src/03_rfm_segmentation.py # RFM + KMeans -> data/segments.json
python src/04_insights.py         # KPIs, findings, recommendations
python src/05_build_dashboard.py  # -> dashboard/index.html
```

Then open `dashboard/index.html` in any browser.

## Repository layout

```
ecommerce-segmentation/
├── data/            # raw + clean data, SQLite db, analysis JSON artifacts
├── sql/             # analysis.sql (documented business queries)
├── src/             # 01–05 pipeline scripts
├── dashboard/       # index.html — the live dashboard
└── README.md
```

## Notes & caveats

- December 2011 is a **partial month** (data ends 2011-12-09); its month-over-month drop is a data artifact, not a real decline — flagged in the dashboard.
- Only transactions with a `CustomerID` are used, since the whole project is customer-centric; anonymous sales are out of scope by design.

---

*Built by Vishali A — Data Analyst (Python · SQL · Data Visualization).*
