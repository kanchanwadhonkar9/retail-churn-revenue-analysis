# Dashboard deliverable

The primary dashboard artifact is [`retail_churn_dashboard.html`](retail_churn_dashboard.html), a self-contained interactive view that runs in a browser. It includes contract, internet-service, payment-method, and tenure-band filters; KPI cards for customers, churn rate, monthly revenue, revenue at risk, and average observed customer value; plus charts for churn by contract, retention by tenure band, revenue at risk by internet service, and churn by payment method.

The screenshot [`dashboard_overview.webp`](dashboard_overview.webp) is included for README preview. The cleaned CSV and SQLite database are import-ready for Power BI or Tableau. A native `.pbix`/`.twbx` binary is not included because those files are desktop-authoring binaries; the browser dashboard is the reproducible interactive equivalent, and the repository contains the full source data model, field logic, and refresh scripts.

## KPI definitions

| KPI | Definition |
|---|---|
| Churn rate | Churned customers divided by selected customer records. |
| Monthly revenue | Sum of cleaned `monthly_charges`. |
| Revenue at risk | Sum of `monthly_charges` for customers with `churn_flag = 1`. |
| Average observed CLV | Mean of cleaned `estimated_clv`, which equals observed `total_charges`. |
| Retention trend | Retention rate by tenure band because the source snapshot has no calendar date. |

To rebuild the dashboard after refreshing the cleaned data, run `python src/build_analysis.py`, `python src/load_sqlite.py`, and `python src/build_dashboard.py` from the repository root.
