# Data

The raw dataset is not committed (≈45 MB). Download it and place `online_retail.csv` here:

- UCI: https://archive.ics.uci.edu/dataset/352/online+retail
- Then run `python src/01_clean.py` to regenerate the clean tables.

The small JSON artifacts (`*_audit.json`, `sql_results.json`, `segments.json`,
`insights.json`) that feed the dashboard are included so the dashboard builds
without re-downloading.
