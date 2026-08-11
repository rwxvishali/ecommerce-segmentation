"""
03_rfm_segmentation.py — Customer segmentation via RFM + KMeans.

Two complementary views:
  (A) Rule-based RFM scoring -> business-friendly named segments
      (Champions, Loyal, At Risk, ...). Transparent, easy to explain to marketing.
  (B) Unsupervised KMeans on standardized log(RFM) -> data-driven clusters,
      with k chosen by silhouette score. Catches structure rules might miss.

Outputs data/segments.json (feeds the dashboard) and data/rfm.csv.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
RANDOM_STATE = 42

def build_rfm(df):
    snapshot = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda s: (snapshot - s.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum"),
    ).reset_index()
    rfm = rfm[rfm["Monetary"] > 0]
    return rfm, snapshot

def rule_based_segments(rfm):
    """Classic 1-5 quantile RFM scoring -> named segments."""
    r = rfm.copy()
    r["R"] = pd.qcut(r["Recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)   # recent = high
    r["F"] = pd.qcut(r["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    r["M"] = pd.qcut(r["Monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    r["RFM_Score"] = r["R"] + r["F"] + r["M"]

    def label(row):
        R, F, M = row["R"], row["F"], row["M"]
        FM = (F + M) / 2
        if R >= 4 and FM >= 4: return "Champions"
        if R >= 3 and FM >= 3: return "Loyal Customers"
        if R >= 4 and FM <= 2: return "New / Promising"
        if R == 3 and FM <= 2: return "Potential Loyalists"
        if R <= 2 and FM >= 4: return "At Risk (high value)"
        if R <= 2 and FM == 3: return "Needs Attention"
        if R <= 2 and FM <= 2: return "Hibernating / Lost"
        return "Others"

    r["Segment"] = r.apply(label, axis=1)
    return r

def kmeans_clusters(rfm):
    """KMeans on standardized log-RFM; pick k by silhouette."""
    X = rfm[["Recency", "Frequency", "Monetary"]].copy()
    Xlog = np.log1p(X)                      # tame heavy right-skew
    Xs = StandardScaler().fit_transform(Xlog)

    scores = {}
    best_k, best_model, best_sil = None, None, -1
    for k in range(3, 8):
        km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE)
        labels = km.fit_predict(Xs)
        sil = silhouette_score(Xs, labels)
        scores[k] = round(float(sil), 4)
        if sil > best_sil:
            best_k, best_model, best_sil = k, km, sil

    rfm = rfm.copy()
    rfm["Cluster"] = best_model.fit_predict(Xs)

    # Name clusters by their mean RFM (data-driven -> human label)
    prof = rfm.groupby("Cluster").agg(
        n=("CustomerID", "size"),
        Recency=("Recency", "mean"),
        Frequency=("Frequency", "mean"),
        Monetary=("Monetary", "mean"),
    )
    # rank: lower recency = better; higher freq & monetary = better
    prof["value_rank"] = (prof["Monetary"].rank() + prof["Frequency"].rank()
                          + (len(prof) + 1 - prof["Recency"].rank()))
    order = prof["value_rank"].sort_values(ascending=False).index.tolist()
    names = ["VIP / Best", "Loyal Regulars", "Steady Mid-Tier",
             "Occasional Buyers", "Dormant / Low-Value", "Cold / Churned",
             "Fringe"]
    cluster_name = {cid: names[i] for i, cid in enumerate(order)}
    rfm["ClusterName"] = rfm["Cluster"].map(cluster_name)
    return rfm, scores, best_k, best_sil, cluster_name

def main():
    df = pd.read_parquet(DATA / "clean.parquet")
    rfm, snapshot = build_rfm(df)

    ruled = rule_based_segments(rfm)
    clustered, sil_scores, best_k, best_sil, cluster_name = kmeans_clusters(rfm)

    merged = ruled.merge(clustered[["CustomerID", "Cluster", "ClusterName"]], on="CustomerID")
    merged.to_csv(DATA / "rfm.csv", index=False)

    # ---- Segment summaries for the dashboard ----
    total_rev = float(merged["Monetary"].sum())

    def summarize(group_col):
        g = merged.groupby(group_col).agg(
            customers=("CustomerID", "size"),
            avg_recency=("Recency", "mean"),
            avg_frequency=("Frequency", "mean"),
            avg_monetary=("Monetary", "mean"),
            total_revenue=("Monetary", "sum"),
        ).reset_index()
        g["pct_customers"] = 100 * g["customers"] / g["customers"].sum()
        g["pct_revenue"] = 100 * g["total_revenue"] / total_rev
        for c in ["avg_recency", "avg_frequency", "avg_monetary", "total_revenue",
                  "pct_customers", "pct_revenue"]:
            g[c] = g[c].round(2)
        return g.sort_values("total_revenue", ascending=False).to_dict(orient="records")

    out = {
        "meta": {
            "snapshot_date": str(snapshot.date()),
            "n_customers": int(len(merged)),
            "kmeans_best_k": int(best_k),
            "kmeans_silhouette": round(float(best_sil), 4),
            "kmeans_silhouette_by_k": sil_scores,
        },
        "rule_based_segments": summarize("Segment"),
        "kmeans_segments": summarize("ClusterName"),
        # scatter sample for the dashboard (cap size for a light payload)
        "scatter": merged.sample(min(1500, len(merged)), random_state=RANDOM_STATE)[
            ["Recency", "Frequency", "Monetary", "ClusterName", "Segment"]
        ].round(2).to_dict(orient="records"),
    }
    with open(DATA / "segments.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"snapshot={out['meta']['snapshot_date']}  customers={out['meta']['n_customers']}")
    print(f"KMeans best k={best_k}  silhouette={best_sil:.3f}  by_k={sil_scores}")
    print("\n-- Rule-based segments --")
    for s in out["rule_based_segments"]:
        print(f"  {s['Segment']:<24} n={s['customers']:>4}  "
              f"{s['pct_customers']:>5.1f}% cust  {s['pct_revenue']:>5.1f}% rev  "
              f"avgM £{s['avg_monetary']:,.0f}")
    print("\n-- KMeans clusters --")
    for s in out["kmeans_segments"]:
        print(f"  {s['ClusterName']:<22} n={s['customers']:>4}  "
              f"R={s['avg_recency']:>5.0f}d F={s['avg_frequency']:>4.1f} "
              f"M=£{s['avg_monetary']:>8,.0f}  {s['pct_revenue']:>5.1f}% rev")

if __name__ == "__main__":
    main()
