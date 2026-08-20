from pathlib import Path
import json
import re
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
required = [
    'README.md', 'requirements.txt',
    'data/raw/Telco-Customer-Churn.csv', 'data/raw/SOURCE.md',
    'data/cleaned/telco_customer_churn_cleaned.csv', 'data/cleaned/cleaning_log.json', 'data/cleaned/retail_churn.sqlite',
    'notebooks/01_data_cleaning.ipynb', 'notebooks/02_business_analysis.ipynb',
    'sql/schema.sql', 'sql/business_questions.sql', 'sql/README.md',
    'dashboard/retail_churn_dashboard.html', 'dashboard/dashboard_overview.webp', 'dashboard/README.md',
    'reports/business_impact_report.md', 'reports/analysis_summary.json', 'reports/sql_validation.json',
    'visuals/churn_by_contract.png', 'visuals/churn_by_tenure.png', 'visuals/churn_by_internet_service.png', 'visuals/tenure_vs_monthly_charges.png',
]
missing = [p for p in required if not (ROOT / p).exists()]
assert not missing, f'Missing required files: {missing}'

raw = pd.read_csv(ROOT / 'data/raw/Telco-Customer-Churn.csv')
cleaned = pd.read_csv(ROOT / 'data/cleaned/telco_customer_churn_cleaned.csv')
log = json.loads((ROOT / 'data/cleaned/cleaning_log.json').read_text())
assert len(raw) == 7043 and len(cleaned) == 7043
assert log['percent_of_rows_requiring_cleaning'] == 0.16
assert int(cleaned['customer_id'].nunique()) == 7043

sql_text = (ROOT / 'sql/business_questions.sql').read_text()
query_count = len(re.findall(r'^-- Q\d{2}\.', sql_text, flags=re.MULTILINE))
assert query_count == 14
sql_validation = json.loads((ROOT / 'reports/sql_validation.json').read_text())
assert len(sql_validation) == 14 and all(r['rows_returned'] > 0 for r in sql_validation)

for notebook in ['notebooks/01_data_cleaning.ipynb', 'notebooks/02_business_analysis.ipynb']:
    payload = json.loads((ROOT / notebook).read_text())
    assert payload['nbformat'] == 4 and len(payload['cells']) >= 5

with sqlite3.connect(ROOT / 'data/cleaned/retail_churn.sqlite') as conn:
    count = conn.execute('SELECT COUNT(*) FROM customer_churn').fetchone()[0]
    assert count == 7043

html = (ROOT / 'dashboard/retail_churn_dashboard.html').read_text()
for token in ['kpiCustomers', 'kpiChurn', 'kpiRevenue', 'kpiRisk', 'kpiClv', 'contractChart', 'tenureChart', 'internetChart', 'paymentChart']:
    assert token in html

print(json.dumps({
    'required_files': len(required),
    'raw_rows': len(raw),
    'cleaned_rows': len(cleaned),
    'cleaning_percent': log['percent_of_rows_requiring_cleaning'],
    'sql_queries': query_count,
    'sql_queries_with_rows': len(sql_validation),
    'sqlite_rows': count,
    'status': 'PASS'
}, indent=2))
