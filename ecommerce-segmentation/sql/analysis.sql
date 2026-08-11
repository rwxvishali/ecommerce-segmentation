-- =====================================================================
--  Online Retail — Business Analysis (SQLite)
--  Table: retail(InvoiceNo, StockCode, Description, Quantity, InvoiceDate,
--                UnitPrice, CustomerID, Country, Revenue, InvoiceYearMonth)
--  Each query answers a specific business question a stakeholder would ask.
-- =====================================================================

-- Q1. What is the monthly revenue trend, and how is it growing month-over-month?
--     (window function LAG for MoM growth)
WITH monthly AS (
    SELECT InvoiceYearMonth AS ym,
           ROUND(SUM(Revenue), 2) AS revenue,
           COUNT(DISTINCT InvoiceNo) AS orders,
           COUNT(DISTINCT CustomerID) AS active_customers
    FROM retail
    GROUP BY InvoiceYearMonth
)
SELECT ym, revenue, orders, active_customers,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY ym))
             / LAG(revenue) OVER (ORDER BY ym), 1) AS mom_growth_pct
FROM monthly
ORDER BY ym;

-- Q2. Which 10 markets (countries) drive the most revenue, and what share of total?
SELECT Country,
       ROUND(SUM(Revenue), 2) AS revenue,
       COUNT(DISTINCT CustomerID) AS customers,
       ROUND(100.0 * SUM(Revenue) / (SELECT SUM(Revenue) FROM retail), 1) AS pct_of_total
FROM retail
GROUP BY Country
ORDER BY revenue DESC
LIMIT 10;

-- Q3. What are the top 10 products by revenue?
SELECT StockCode,
       MAX(Description) AS description,
       SUM(Quantity)   AS units_sold,
       ROUND(SUM(Revenue), 2) AS revenue
FROM retail
GROUP BY StockCode
ORDER BY revenue DESC
LIMIT 10;

-- Q4. How concentrated is revenue? (Pareto — share from top 20% of customers)
WITH cust AS (
    SELECT CustomerID, SUM(Revenue) AS spend
    FROM retail GROUP BY CustomerID
),
ranked AS (
    SELECT CustomerID, spend,
           NTILE(5) OVER (ORDER BY spend DESC) AS quintile
    FROM cust
)
SELECT quintile,
       COUNT(*) AS customers,
       ROUND(SUM(spend), 2) AS revenue,
       ROUND(100.0 * SUM(spend) / (SELECT SUM(spend) FROM cust), 1) AS pct_of_revenue
FROM ranked
GROUP BY quintile
ORDER BY quintile;

-- Q5. Repeat-purchase rate: what share of customers bought more than once?
WITH orders_per_cust AS (
    SELECT CustomerID, COUNT(DISTINCT InvoiceNo) AS n_orders
    FROM retail GROUP BY CustomerID
)
SELECT
    COUNT(*)                                              AS total_customers,
    SUM(CASE WHEN n_orders > 1 THEN 1 ELSE 0 END)         AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN n_orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS repeat_rate_pct,
    ROUND(AVG(n_orders), 2)                               AS avg_orders_per_customer
FROM orders_per_cust;

-- Q6. Average Order Value overall.
SELECT ROUND(SUM(Revenue) / COUNT(DISTINCT InvoiceNo), 2) AS avg_order_value
FROM retail;
