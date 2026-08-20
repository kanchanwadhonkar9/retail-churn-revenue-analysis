# SQL layer

The SQLite data model is stored at `data/cleaned/retail_churn.sqlite`. The table `customer_churn` contains one row per customer plus derived business fields for churn flag, retention flag, tenure band, observed customer value, monthly revenue at risk, and service bundle.

The file `business_questions.sql` contains 14 commented queries. They answer headline KPI, contract, revenue mix, internet service, payment method, tenure retention, customer value, revenue-at-risk, service bundle, household segment, support, CLV quartile, and prioritization questions. Run the file with:

```bash
sqlite3 data/cleaned/retail_churn.sqlite < sql/business_questions.sql
```

Because the source is a customer snapshot without a calendar date, a true month-over-month revenue trend is not statistically supportable. The project uses retention by tenure band as the defensible trend view and states this limitation in the dashboard and README.
