from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
raw_path = ROOT / 'data' / 'raw' / 'Telco-Customer-Churn.csv'
df = pd.read_csv(raw_path)
print('shape', df.shape)
print('duplicates', int(df.duplicated().sum()))
print('missing')
print(df.isna().sum().to_string())
print('blank_total_charges', int(df['TotalCharges'].astype(str).str.strip().eq('').sum()))
for col in ['MonthlyCharges', 'TotalCharges']:
    s = pd.to_numeric(df[col].replace(r'^\s*$', pd.NA, regex=True), errors='coerce').dropna()
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    print(col, 'q1', q1, 'q3', q3, 'lower', lower, 'upper', upper, 'outliers', int(((s < lower) | (s > upper)).sum()))
print('unique_customer_ids', df['customerID'].nunique())
print('churn', df['Churn'].value_counts(dropna=False).to_dict())
