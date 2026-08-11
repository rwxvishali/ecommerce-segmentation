# E-commerce Customer Segmentation & Analytics

End-to-end data analytics project — turning 541,909 raw online-retail transactions into customer segments and a live dashboard.

**Built with:** Python (pandas, scikit-learn) · SQL · interactive HTML dashboard

## Key results
- Cleaned **541K transactions** → £8.74M revenue across 4,334 customers
- **Top 20% of customers drive 74.6% of revenue** (Pareto concentration)
- **65.3% repeat-purchase rate**
- Segmented customers with **RFM scoring + KMeans clustering** (k chosen by silhouette score) — found a **686-customer VIP group that alone drives 64% of revenue**
- Identified **£510K of "at-risk" revenue** and costed win-back actions

## What's inside
- `ecommerce-segmentation/src/` — Python pipeline (cleaning → SQL → segmentation → dashboard)
- `ecommerce-segmentation/sql/` — business analysis queries (CTEs, window functions)
- `ecommerce-segmentation/dashboard/index.html` — the live interactive dashboard

*Dataset: UCI / Kaggle Online Retail. Built by Vishali A — Data Analyst (Python · SQL · Data Visualization).*
