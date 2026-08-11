"""
04_insights.py — Turn the analysis into a compact set of KPIs, findings, and
costed recommendations. Saves data/insights.json for the dashboard + README.
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"

def load(name):
    with open(DATA / name) as f:
        return json.load(f)

def main():
    audit = load("cleaning_audit.json")
    sqlr = load("sql_results.json")
    seg = load("segments.json")

    total_rev = audit["total_revenue"]
    aov = sqlr["aov"][0]["avg_order_value"]
    repeat = sqlr["repeat_rate"][0]
    pareto_top = sqlr["pareto_quintiles"][0]  # top quintile

    rule = {s["Segment"]: s for s in seg["rule_based_segments"]}
    km = {s["ClusterName"]: s for s in seg["kmeans_segments"]}

    champions = rule.get("Champions", {})
    at_risk = rule.get("At Risk (high value)", {})
    hibernating = rule.get("Hibernating / Lost", {})
    vip = km.get("VIP / Best", {})

    kpis = [
        {"label": "Total Revenue", "value": f"£{total_rev/1e6:.2f}M", "sub": f"{audit['date_min']} to {audit['date_max']}"},
        {"label": "Customers", "value": f"{audit['final_customers']:,}", "sub": f"{audit['final_orders']:,} orders"},
        {"label": "Avg Order Value", "value": f"£{aov:,.0f}", "sub": "across all markets"},
        {"label": "Repeat Rate", "value": f"{repeat['repeat_rate_pct']}%", "sub": f"{repeat['avg_orders_per_customer']} orders/customer"},
    ]

    findings = [
        f"Revenue is highly concentrated: the top 20% of customers generate "
        f"{pareto_top['pct_of_revenue']}% of all revenue (£{pareto_top['revenue']/1e6:.2f}M).",
        f"KMeans isolates a VIP cluster of {vip.get('customers','?')} customers "
        f"(avg {vip.get('avg_frequency','?')} orders, £{vip.get('avg_monetary',0):,.0f} each) "
        f"that alone drives {vip.get('pct_revenue','?')}% of revenue.",
        f"{repeat['repeat_rate_pct']}% of customers are repeat buyers — a strong, "
        f"retention-friendly base to build loyalty programs on.",
        f"The UK accounts for {sqlr['top_countries'][0]['pct_of_total']}% of revenue; "
        f"international markets (Netherlands, EIRE, Germany, France) are small but proven — a growth lever.",
        f"£{at_risk.get('total_revenue',0):,.0f} of annual revenue sits in the "
        f"'At Risk (high value)' segment — {at_risk.get('customers','?')} formerly strong "
        f"customers who have gone quiet.",
    ]

    # Simple, clearly-stated win-back opportunity sizing.
    at_risk_rev = at_risk.get("total_revenue", 0)
    winback_20 = round(at_risk_rev * 0.20)
    recommendations = [
        {"segment": "Champions / VIP",
         "action": "Protect & reward: early access, VIP tier, personal account care.",
         "why": f"{champions.get('customers','?')} customers ≈ {champions.get('pct_revenue','?')}% of revenue. "
                "Churn here is the single biggest financial risk."},
        {"segment": "At Risk (high value)",
         "action": "Win-back campaign: targeted re-engagement offer + 'we miss you' outreach.",
         "why": f"£{at_risk_rev:,.0f} of revenue at stake. Recovering just 20% is "
                f"≈ £{winback_20:,.0f}/yr for the cost of one email campaign."},
        {"segment": "Loyal / Potential Loyalists",
         "action": "Nurture up: cross-sell bundles and a points program to push toward Champion status.",
         "why": "Largest mid-tier group — the pipeline that replenishes the VIP base."},
        {"segment": "Hibernating / Lost",
         "action": "Low-cost reactivation only (automated flows); don't over-invest.",
         "why": f"{hibernating.get('customers','?')} customers but only {hibernating.get('pct_revenue','?')}% of "
                "revenue — cap spend and let most lapse."},
    ]

    out = {"kpis": kpis, "findings": findings, "recommendations": recommendations,
           "notes": ["Dec 2011 is a partial month (data ends 2011-12-09); its month-over-month drop is a data artifact, not a real decline."]}
    with open(DATA / "insights.json", "w") as f:
        json.dump(out, f, indent=2)

    print("KPIs:", [k["value"] for k in kpis])
    print("\nFindings:")
    for x in findings: print(" -", x)
    print("\nRecommendations:")
    for r in recommendations: print(f" - [{r['segment']}] {r['action']}")

if __name__ == "__main__":
    main()
