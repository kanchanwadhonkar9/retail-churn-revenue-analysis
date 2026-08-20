from pathlib import Path
import json
import re
import sqlite3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / 'data' / 'raw' / 'Telco-Customer-Churn.csv'
CLEAN_DIR = ROOT / 'data' / 'cleaned'
VIS_DIR = ROOT / 'visuals'
REPORT_DIR = ROOT / 'reports'
for path in [CLEAN_DIR, VIS_DIR, REPORT_DIR]:
    path.mkdir(parents=True, exist_ok=True)

sns.set_theme(style='whitegrid', context='talk')
PALETTE = {'Yes': '#E45756', 'No': '#2A9D8F', 'accent': '#264653', 'gold': '#F4A261'}


def snake_case(value: str) -> str:
    value = re.sub(r'(?<!^)(?=[A-Z])', '_', value)
    value = re.sub(r'[^0-9a-zA-Z]+', '_', value).strip('_').lower()
    return value


def iqr_bounds(series: pd.Series):
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def pct(value, total):
    return round((value / total) * 100, 2) if total else 0.0


# 1. Load and standardize the raw public dataset.
raw = pd.read_csv(RAW_PATH)
raw_rows, raw_cols = raw.shape
raw_duplicate_rows = int(raw.duplicated().sum())
raw_blank_total_charges = int(raw['TotalCharges'].astype(str).str.strip().eq('').sum())

# Preserve a raw copy for the data-quality audit, then normalize names and whitespace.
df = raw.drop_duplicates().copy()
df.columns = [snake_case(c) for c in df.columns]
df = df.rename(columns={'customer_i_d': 'customer_id'})
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].astype('string').str.strip()
    df[col] = df[col].replace({'': pd.NA, 'nan': pd.NA, 'None': pd.NA})

# Correct data types; blank TotalCharges values become numeric missing values.
numeric_cols = ['senior_citizen', 'tenure', 'monthly_charges', 'total_charges']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Track each repair so the percentage cleaned is auditable.
df['quality_missing_total_charges'] = df['total_charges'].isna()
# For the 0-tenure new customers, total recurring charges are logically 0.
impute_mask = df['total_charges'].isna() & df['tenure'].eq(0)
df.loc[impute_mask, 'total_charges'] = 0.0
# If any other missing values ever appear, use median for numeric and Unknown for categorical.
for col in ['senior_citizen', 'tenure', 'monthly_charges']:
    df[col] = df[col].fillna(df[col].median())
for col in df.select_dtypes(include=['object', 'string']).columns:
    if not col.startswith('quality_'):
        df[col] = df[col].fillna('Unknown')

# Enforce business-valid ranges and winsorize statistical outliers.
quality_flags = pd.DataFrame(index=df.index)
quality_flags['invalid_tenure'] = ~df['tenure'].between(0, 72)
quality_flags['invalid_monthly_charges'] = df['monthly_charges'].lt(0)
quality_flags['invalid_total_charges'] = df['total_charges'].lt(0)

df['tenure'] = df['tenure'].clip(0, 72)
df['monthly_charges'] = df['monthly_charges'].clip(lower=0)
df['total_charges'] = df['total_charges'].clip(lower=0)

for col in ['monthly_charges', 'total_charges']:
    lower, upper = iqr_bounds(df[col])
    flag = (df[col] < lower) | (df[col] > upper)
    quality_flags[f'{col}_iqr_outlier'] = flag
    df[f'{col}_original'] = df[col]
    df[col] = df[col].clip(lower, upper)

# Customer-level business fields used by SQL and dashboard layers.
df['churn_flag'] = df['churn'].eq('Yes').astype(int)
df['retained_flag'] = 1 - df['churn_flag']
df['customer_type'] = np.where(df['senior_citizen'].eq(1), 'Senior Citizen', 'Non-Senior')
df['tenure_band'] = pd.cut(
    df['tenure'], bins=[-1, 12, 24, 48, np.inf],
    labels=['0-12 months', '13-24 months', '25-48 months', '49+ months']
).astype(str)
df['estimated_clv'] = df['total_charges'].round(2)
df['monthly_revenue_at_risk'] = np.where(df['churn_flag'].eq(1), df['monthly_charges'], 0.0).round(2)
df['service_bundle'] = np.select(
    [
        df['internet_service'].eq('No'),
        df['online_security'].eq('Yes') & df['tech_support'].eq('Yes'),
    ],
    ['Phone Only', 'Protected Internet'],
    default='Standard Internet'
)

# Remove helper originals from the analyst-facing file while preserving audit results separately.
helper_cols = ['monthly_charges_original', 'total_charges_original']
cleaned = df.drop(columns=helper_cols)

row_repair_mask = (
    df['quality_missing_total_charges']
    | quality_flags.any(axis=1)
)
cleaning_rows = int(row_repair_mask.sum())
cleaning_log = {
    'source': 'IBM Telco Customer Churn sample; Kaggle listing: https://www.kaggle.com/datasets/blastchar/telco-customer-churn',
    'raw_rows': raw_rows,
    'raw_columns': raw_cols,
    'cleaned_rows': int(cleaned.shape[0]),
    'cleaned_columns': int(cleaned.shape[1]),
    'exact_duplicate_rows_removed': raw_duplicate_rows,
    'blank_total_charges_rows': raw_blank_total_charges,
    'total_charges_imputed_to_zero': int(impute_mask.sum()),
    'rows_requiring_cleaning': cleaning_rows,
    'percent_of_rows_requiring_cleaning': round(pct(cleaning_rows, raw_rows), 4),
    'iqr_outliers': {col: int(quality_flags[f'{col}_iqr_outlier'].sum()) for col in ['monthly_charges', 'total_charges']},
    'invalid_values_after_coercion': {col: int(quality_flags[col].sum()) for col in ['invalid_tenure', 'invalid_monthly_charges', 'invalid_total_charges']},
    'cleaning_method': 'Trim object fields; coerce numeric fields; impute zero-tenure blank TotalCharges to 0; impute remaining numeric gaps with median; fill remaining categorical gaps with Unknown; clip logical ranges; winsorize IQR outliers.',
}

cleaned.to_csv(CLEAN_DIR / 'telco_customer_churn_cleaned.csv', index=False)
(CLEAN_DIR / 'cleaning_log.json').write_text(json.dumps(cleaning_log, indent=2))

# 2. Business analysis outputs.
overall = {
    'customers': int(len(cleaned)),
    'churned_customers': int(cleaned['churn_flag'].sum()),
    'retained_customers': int(cleaned['retained_flag'].sum()),
    'churn_rate_pct': round(cleaned['churn_flag'].mean() * 100, 2),
    'monthly_recurring_revenue': round(cleaned['monthly_charges'].sum(), 2),
    'monthly_revenue_at_risk': round(cleaned['monthly_revenue_at_risk'].sum(), 2),
    'observed_customer_value': round(cleaned['estimated_clv'].sum(), 2),
    'avg_observed_customer_value': round(cleaned['estimated_clv'].mean(), 2),
    'avg_monthly_charge': round(cleaned['monthly_charges'].mean(), 2),
    'avg_tenure_months': round(cleaned['tenure'].mean(), 2),
}


def grouped_metrics(group_col):
    result = cleaned.groupby(group_col, dropna=False).agg(
        customers=('customer_id', 'nunique'),
        churned_customers=('churn_flag', 'sum'),
        churn_rate=('churn_flag', 'mean'),
        monthly_revenue=('monthly_charges', 'sum'),
        revenue_at_risk=('monthly_revenue_at_risk', 'sum'),
        avg_monthly_charge=('monthly_charges', 'mean'),
        avg_observed_customer_value=('estimated_clv', 'mean'),
        avg_tenure_months=('tenure', 'mean'),
    ).reset_index()
    result['churn_rate_pct'] = (result['churn_rate'] * 100).round(2)
    result = result.drop(columns='churn_rate')
    for col in ['monthly_revenue', 'revenue_at_risk', 'avg_monthly_charge', 'avg_observed_customer_value', 'avg_tenure_months']:
        result[col] = result[col].round(2)
    return result.sort_values(['churn_rate_pct', 'customers'], ascending=[False, False])

analysis_tables = {}
for dimension in ['contract', 'internet_service', 'payment_method', 'tenure_band', 'customer_type', 'service_bundle']:
    table = grouped_metrics(dimension)
    analysis_tables[dimension] = table
    table.to_csv(REPORT_DIR / f'{dimension}_metrics.csv', index=False)

# Key comparisons used in the README and business recommendations.
contract_metrics = analysis_tables['contract']
month_to_month_rate = float(contract_metrics.loc[contract_metrics['contract'].eq('Month-to-month'), 'churn_rate_pct'].iloc[0])
two_year_rate = float(contract_metrics.loc[contract_metrics['contract'].eq('Two year'), 'churn_rate_pct'].iloc[0])
contract_lift = round(month_to_month_rate / two_year_rate, 2) if two_year_rate else None

tenure_metrics = analysis_tables['tenure_band']
short_tenure_rate = float(tenure_metrics.loc[tenure_metrics['tenure_band'].eq('0-12 months'), 'churn_rate_pct'].iloc[0])
long_tenure_rate = float(tenure_metrics.loc[tenure_metrics['tenure_band'].eq('49+ months'), 'churn_rate_pct'].iloc[0])

internet_metrics = analysis_tables['internet_service']
fiber_rate = float(internet_metrics.loc[internet_metrics['internet_service'].eq('Fiber optic'), 'churn_rate_pct'].iloc[0])
dsl_rate = float(internet_metrics.loc[internet_metrics['internet_service'].eq('DSL'), 'churn_rate_pct'].iloc[0])

payment_metrics = analysis_tables['payment_method']
echeck_rate = float(payment_metrics.loc[payment_metrics['payment_method'].eq('Electronic check'), 'churn_rate_pct'].iloc[0])
non_echeck = payment_metrics.loc[payment_metrics['payment_method'].ne('Electronic check')]
non_echeck_rate = round(float((non_echeck['churned_customers'].sum() / non_echeck['customers'].sum()) * 100), 2)

recommendation_segment = cleaned.loc[
    cleaned['contract'].eq('Month-to-month') & cleaned['payment_method'].eq('Electronic check')
]
recommendation_segment_stats = {
    'customers': int(len(recommendation_segment)),
    'churn_rate_pct': round(recommendation_segment['churn_flag'].mean() * 100, 2),
    'monthly_revenue_at_risk': round(recommendation_segment['monthly_revenue_at_risk'].sum(), 2),
    'annualized_revenue_at_risk': round(recommendation_segment['monthly_revenue_at_risk'].sum() * 12, 2),
}

key_insights = [
    {
        'finding': 'Month-to-month contracts are the highest-risk contract type.',
        'evidence': f"Churn is {month_to_month_rate:.1f}% for month-to-month customers versus {two_year_rate:.1f}% for two-year customers ({contract_lift:.1f}x higher).",
        'metric': month_to_month_rate,
    },
    {
        'finding': 'Churn is concentrated in the first year of tenure.',
        'evidence': f"Customers with 0-12 months tenure churn at {short_tenure_rate:.1f}% versus {long_tenure_rate:.1f}% for 49+ months.",
        'metric': short_tenure_rate,
    },
    {
        'finding': 'Fiber optic customers show elevated churn.',
        'evidence': f"Fiber optic churn is {fiber_rate:.1f}% versus {dsl_rate:.1f}% for DSL, a {fiber_rate - dsl_rate:.1f} percentage-point gap.",
        'metric': fiber_rate,
    },
    {
        'finding': 'Electronic-check customers are a high-priority payment-friction segment.',
        'evidence': f"Electronic-check churn is {echeck_rate:.1f}% versus {non_echeck_rate:.1f}% for other payment methods.",
        'metric': echeck_rate,
    },
]

analysis_summary = {
    'overall': overall,
    'key_insights': key_insights,
    'recommendation_segment': recommendation_segment_stats,
    'definitions': {
        'estimated_clv': 'Observed customer value proxy equal to cleaned TotalCharges; the public snapshot does not include margin, discount, or future-survival assumptions.',
        'retention_trend': 'Retention by tenure band, because this snapshot has no transaction date or acquisition cohort date for calendar month-over-month analysis.',
    },
}
(REPORT_DIR / 'analysis_summary.json').write_text(json.dumps(analysis_summary, indent=2))

# 3. Publication-quality static visuals.
fig, ax = plt.subplots(figsize=(10, 6))
plot = contract_metrics.sort_values('churn_rate_pct')
sns.barplot(data=plot, x='churn_rate_pct', y='contract', palette=[PALETTE['accent'], PALETTE['gold'], PALETTE['accent']], ax=ax, hue='contract', legend=False)
ax.set_title('Churn rate by contract type', loc='left', weight='bold')
ax.set_xlabel('Churn rate (%)')
ax.set_ylabel('')
for i, val in enumerate(plot['churn_rate_pct']):
    ax.text(val + 0.8, i, f'{val:.1f}%', va='center', fontsize=11)
fig.tight_layout()
fig.savefig(VIS_DIR / 'churn_by_contract.png', dpi=180, bbox_inches='tight')
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 6))
plot = tenure_metrics.sort_values('tenure_band')
sns.lineplot(data=plot, x='tenure_band', y='churn_rate_pct', marker='o', linewidth=3, color=PALETTE['accent'], ax=ax)
ax.set_title('Retention risk declines with tenure', loc='left', weight='bold')
ax.set_xlabel('Tenure band')
ax.set_ylabel('Churn rate (%)')
ax.tick_params(axis='x', rotation=20)
fig.tight_layout()
fig.savefig(VIS_DIR / 'churn_by_tenure.png', dpi=180, bbox_inches='tight')
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 6))
plot = internet_metrics.sort_values('churn_rate_pct')
sns.barplot(data=plot, x='churn_rate_pct', y='internet_service', palette=[PALETTE['accent'], PALETTE['gold'], PALETTE['accent']], ax=ax, hue='internet_service', legend=False)
ax.set_title('Churn rate by internet service', loc='left', weight='bold')
ax.set_xlabel('Churn rate (%)')
ax.set_ylabel('')
for i, val in enumerate(plot['churn_rate_pct']):
    ax.text(val + 0.8, i, f'{val:.1f}%', va='center', fontsize=11)
fig.tight_layout()
fig.savefig(VIS_DIR / 'churn_by_internet_service.png', dpi=180, bbox_inches='tight')
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=cleaned.sample(min(1800, len(cleaned)), random_state=42), x='tenure', y='monthly_charges', hue='churn', palette=PALETTE, alpha=0.45, ax=ax)
ax.set_title('Customer value and churn distribution', loc='left', weight='bold')
ax.set_xlabel('Tenure (months)')
ax.set_ylabel('Monthly charges ($)')
ax.legend(title='Churn', frameon=True)
fig.tight_layout()
fig.savefig(VIS_DIR / 'tenure_vs_monthly_charges.png', dpi=180, bbox_inches='tight')
plt.close(fig)

print(json.dumps({'cleaning': cleaning_log, 'overall': overall, 'recommendation_segment': recommendation_segment_stats}, indent=2))
