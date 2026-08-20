from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN_PATH = ROOT / 'data' / 'cleaned' / 'telco_customer_churn_cleaned.csv'
DB_PATH = ROOT / 'data' / 'cleaned' / 'retail_churn.sqlite'
SCHEMA_PATH = ROOT / 'sql' / 'schema.sql'

SCHEMA = '''
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
'''

SCHEMA_PATH.write_text(SCHEMA.strip() + '\n')
df = pd.read_csv(CLEAN_PATH)
with sqlite3.connect(DB_PATH) as conn:
    conn.executescript(SCHEMA)
    df.to_sql('customer_churn', conn, if_exists='append', index=False)
    conn.execute('CREATE VIEW IF NOT EXISTS customer_churn_summary AS SELECT * FROM customer_churn')
    conn.commit()
    count = conn.execute('SELECT COUNT(*) FROM customer_churn').fetchone()[0]
    unique_ids = conn.execute('SELECT COUNT(DISTINCT customer_id) FROM customer_churn').fetchone()[0]
print({'database': str(DB_PATH), 'rows_loaded': count, 'unique_customer_ids': unique_ids})
