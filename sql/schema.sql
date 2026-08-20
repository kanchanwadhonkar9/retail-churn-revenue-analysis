DROP TABLE IF EXISTS customer_churn;
CREATE TABLE customer_churn (
    customer_id TEXT PRIMARY KEY,
    gender TEXT NOT NULL,
    senior_citizen INTEGER NOT NULL,
    partner TEXT NOT NULL,
    dependents TEXT NOT NULL,
    tenure INTEGER NOT NULL,
    phone_service TEXT NOT NULL,
    multiple_lines TEXT NOT NULL,
    internet_service TEXT NOT NULL,
    online_security TEXT NOT NULL,
    online_backup TEXT NOT NULL,
    device_protection TEXT NOT NULL,
    tech_support TEXT NOT NULL,
    streaming_t_v TEXT NOT NULL,
    streaming_movies TEXT NOT NULL,
    contract TEXT NOT NULL,
    paperless_billing TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    monthly_charges REAL NOT NULL,
    total_charges REAL NOT NULL,
    churn TEXT NOT NULL,
    quality_missing_total_charges INTEGER NOT NULL,
    churn_flag INTEGER NOT NULL,
    retained_flag INTEGER NOT NULL,
    customer_type TEXT NOT NULL,
    tenure_band TEXT NOT NULL,
    estimated_clv REAL NOT NULL,
    monthly_revenue_at_risk REAL NOT NULL,
    service_bundle TEXT NOT NULL
);
CREATE INDEX idx_customer_churn_contract ON customer_churn(contract);
CREATE INDEX idx_customer_churn_churn ON customer_churn(churn);
CREATE INDEX idx_customer_churn_tenure_band ON customer_churn(tenure_band);
CREATE INDEX idx_customer_churn_payment_method ON customer_churn(payment_method);
