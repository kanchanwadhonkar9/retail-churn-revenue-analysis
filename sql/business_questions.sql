-- Retail Customer Churn & Revenue Analysis
-- Business-question SQL layer (SQLite)
-- Source table: customer_churn
-- Note: the dataset is a customer snapshot with no calendar transaction date.
-- Therefore, retention trend is represented by tenure_band rather than month-over-month calendar cohorts.

-- Q01. What are the headline portfolio KPIs?
SELECT
    COUNT(DISTINCT customer_id) AS customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) AS monthly_recurring_revenue,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk,
    ROUND(AVG(estimated_clv), 2) AS average_observed_customer_value
FROM customer_churn;

-- Q02. Which contract type has the highest churn rate?
SELECT
    contract,
    COUNT(*) AS customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) AS monthly_revenue,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk
FROM customer_churn
GROUP BY contract
ORDER BY churn_rate_pct DESC;

-- Q03. How does monthly revenue distribute across contract types?
SELECT
    contract,
    ROUND(SUM(monthly_charges), 2) AS monthly_revenue,
    ROUND(100.0 * SUM(monthly_charges) / (SELECT SUM(monthly_charges) FROM customer_churn), 2) AS revenue_mix_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charge
FROM customer_churn
GROUP BY contract
ORDER BY monthly_revenue DESC;

-- Q04. Is churn elevated for any internet-service group?
SELECT
    internet_service,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charge
FROM customer_churn
GROUP BY internet_service
ORDER BY churn_rate_pct DESC;

-- Q05. Which payment methods correlate with higher churn?
SELECT
    payment_method,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk
FROM customer_churn
GROUP BY payment_method
ORDER BY churn_rate_pct DESC;

-- Q06. What does the retention trend look like across tenure bands?
SELECT
    tenure_band,
    MIN(tenure) AS min_tenure_months,
    MAX(tenure) AS max_tenure_months,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(retained_flag), 2) AS retention_rate_pct,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct
FROM customer_churn
GROUP BY tenure_band
ORDER BY min_tenure_months;

-- Q07. Which customers have the highest observed customer value (CLV proxy)?
SELECT
    customer_id,
    contract,
    tenure,
    ROUND(estimated_clv, 2) AS observed_customer_value,
    ROUND(monthly_charges, 2) AS monthly_charges,
    churn
FROM customer_churn
ORDER BY estimated_clv DESC
LIMIT 10;

-- Q08. Which churned customers represent the largest monthly revenue-at-risk?
SELECT
    customer_id,
    contract,
    internet_service,
    payment_method,
    tenure,
    ROUND(monthly_charges, 2) AS monthly_revenue_at_risk,
    ROUND(estimated_clv, 2) AS observed_customer_value
FROM customer_churn
WHERE churn = 'Yes'
ORDER BY monthly_revenue_at_risk DESC
LIMIT 10;

-- Q09. Which service bundle has the strongest retention performance?
SELECT
    service_bundle,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(retained_flag), 2) AS retention_rate_pct,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) AS monthly_revenue
FROM customer_churn
GROUP BY service_bundle
ORDER BY retention_rate_pct DESC;

-- Q10. How does churn vary by customer type and household status?
SELECT
    customer_type,
    partner,
    dependents,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk
FROM customer_churn
GROUP BY customer_type, partner, dependents
HAVING COUNT(*) >= 50
ORDER BY churn_rate_pct DESC;

-- Q11. Where is the greatest recurring revenue exposure by contract?
SELECT
    contract,
    SUM(churn_flag) AS churned_customers,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk,
    ROUND(12.0 * SUM(monthly_revenue_at_risk), 2) AS annualized_revenue_at_risk,
    ROUND(100.0 * SUM(monthly_revenue_at_risk) / (SELECT SUM(monthly_revenue_at_risk) FROM customer_churn), 2) AS risk_mix_pct
FROM customer_churn
GROUP BY contract
ORDER BY monthly_revenue_at_risk DESC;

-- Q12. Do technical-support customers retain better than customers without support?
SELECT
    tech_support,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct,
    ROUND(100.0 * AVG(retained_flag), 2) AS retention_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charge
FROM customer_churn
GROUP BY tech_support
ORDER BY churn_rate_pct;

-- Q13. How does churn vary across observed customer-value quartiles?
WITH ranked AS (
    SELECT
        customer_id,
        churn_flag,
        estimated_clv,
        NTILE(4) OVER (ORDER BY estimated_clv) AS clv_quartile
    FROM customer_churn
)
SELECT
    clv_quartile,
    COUNT(*) AS customers,
    ROUND(MIN(estimated_clv), 2) AS min_observed_value,
    ROUND(MAX(estimated_clv), 2) AS max_observed_value,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct
FROM ranked
GROUP BY clv_quartile
ORDER BY clv_quartile;

-- Q14. Which addressable segment combines high risk and material revenue exposure?
SELECT
    contract,
    internet_service,
    payment_method,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct,
    ROUND(SUM(monthly_revenue_at_risk), 2) AS monthly_revenue_at_risk,
    ROUND(12.0 * SUM(monthly_revenue_at_risk), 2) AS annualized_revenue_at_risk
FROM customer_churn
GROUP BY contract, internet_service, payment_method
HAVING COUNT(*) >= 50
ORDER BY monthly_revenue_at_risk DESC, churn_rate_pct DESC;
