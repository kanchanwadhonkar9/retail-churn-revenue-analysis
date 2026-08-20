from pathlib import Path
import json
import html
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN_PATH = ROOT / 'data' / 'cleaned' / 'telco_customer_churn_cleaned.csv'
OUT_PATH = ROOT / 'dashboard' / 'retail_churn_dashboard.html'

df = pd.read_csv(CLEAN_PATH)
# Keep only fields required by the browser dashboard to make the HTML portable.
records = df[[
    'customer_id', 'contract', 'internet_service', 'payment_method', 'tenure_band',
    'churn_flag', 'retained_flag', 'monthly_charges', 'monthly_revenue_at_risk',
    'estimated_clv', 'tenure'
]].to_dict(orient='records')
for row in records:
    for key, value in list(row.items()):
        if pd.isna(value):
            row[key] = None

payload = json.dumps(records, separators=(',', ':'))
page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Retail Customer Churn & Revenue Analysis</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {{ --navy:#102a43; --ink:#243b53; --muted:#627d98; --teal:#2a9d8f; --coral:#e45756; --gold:#f4a261; --bg:#f5f8fb; --card:#ffffff; --line:#d9e2ec; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color:var(--ink); background:var(--bg); }}
    .wrap {{ max-width:1440px; margin:0 auto; padding:30px 34px 44px; }}
    .hero {{ display:flex; justify-content:space-between; gap:24px; align-items:flex-end; margin-bottom:24px; }}
    .eyebrow {{ color:var(--teal); text-transform:uppercase; letter-spacing:.16em; font-weight:800; font-size:12px; margin-bottom:9px; }}
    h1 {{ margin:0; color:var(--navy); font-size:clamp(30px,4vw,50px); line-height:1.05; max-width:850px; }}
    .sub {{ color:var(--muted); max-width:760px; margin:12px 0 0; font-size:15px; line-height:1.55; }}
    .badge {{ background:var(--navy); color:white; border-radius:999px; padding:9px 14px; font-size:12px; font-weight:700; white-space:nowrap; }}
    .panel {{ background:var(--card); border:1px solid var(--line); border-radius:16px; box-shadow:0 8px 28px rgba(16,42,67,.06); }}
    .filters {{ display:grid; grid-template-columns:repeat(4,minmax(150px,1fr)); gap:14px; padding:18px; margin-bottom:18px; }}
    label {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.08em; font-weight:800; display:block; }}
    select {{ margin-top:7px; width:100%; border:1px solid var(--line); border-radius:10px; padding:11px 12px; color:var(--ink); background:#fff; font-size:14px; }}
    .kpis {{ display:grid; grid-template-columns:repeat(5,minmax(140px,1fr)); gap:14px; margin-bottom:18px; }}
    .kpi {{ padding:18px; }}
    .kpi .label {{ color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:11px; font-weight:800; }}
    .kpi .value {{ color:var(--navy); font-size:28px; font-weight:850; margin-top:9px; }}
    .kpi .note {{ color:var(--muted); font-size:11px; margin-top:6px; }}
    .grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:18px; }}
    .chart-card {{ padding:14px 16px 8px; min-height:390px; }}
    .chart-title {{ color:var(--navy); font-size:16px; font-weight:800; margin:4px 4px 0; }}
    .chart-note {{ color:var(--muted); font-size:12px; margin:4px; }}
    .full {{ grid-column:1/-1; }}
    .insights {{ margin-top:18px; padding:20px 22px; }}
    .insights h2 {{ margin:0 0 10px; color:var(--navy); font-size:20px; }}
    .insights p {{ margin:8px 0; color:var(--ink); line-height:1.55; font-size:14px; }}
    .footer {{ color:var(--muted); font-size:12px; margin-top:20px; line-height:1.5; }}
    @media(max-width:950px) {{ .kpis {{ grid-template-columns:repeat(2,1fr); }} .filters {{ grid-template-columns:repeat(2,1fr); }} .grid {{ grid-template-columns:1fr; }} .full {{ grid-column:auto; }} .hero {{ display:block; }} .badge {{ display:inline-block; margin-top:16px; }} }}
    @media(max-width:560px) {{ .wrap {{ padding:20px 14px 30px; }} .kpis,.filters {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
<div class="wrap">
  <section class="hero">
    <div>
      <div class="eyebrow">Business analysis dashboard</div>
      <h1>Retail Customer Churn &amp; Revenue Analysis</h1>
      <p class="sub">A filterable retention and revenue view built from the public IBM Telco Customer Churn snapshot. Use the controls to isolate customer segments and quantify recurring revenue exposure.</p>
    </div>
    <div class="badge">7,043 customer records</div>
  </section>
  <section class="panel filters">
    <div><label for="contract">Contract</label><select id="contract"><option>All</option></select></div>
    <div><label for="internet">Internet service</label><select id="internet"><option>All</option></select></div>
    <div><label for="payment">Payment method</label><select id="payment"><option>All</option></select></div>
    <div><label for="tenure">Tenure band</label><select id="tenure"><option>All</option></select></div>
  </section>
  <section class="kpis">
    <div class="panel kpi"><div class="label">Customers</div><div class="value" id="kpiCustomers">—</div><div class="note">Unique customer records</div></div>
    <div class="panel kpi"><div class="label">Churn rate</div><div class="value" id="kpiChurn">—</div><div class="note">Share of selected customers</div></div>
    <div class="panel kpi"><div class="label">Monthly revenue</div><div class="value" id="kpiRevenue">—</div><div class="note">Recurring charge run-rate</div></div>
    <div class="panel kpi"><div class="label">Revenue at risk</div><div class="value" id="kpiRisk">—</div><div class="note">Churned monthly charges</div></div>
    <div class="panel kpi"><div class="label">Avg observed CLV</div><div class="value" id="kpiClv">—</div><div class="note">TotalCharges proxy</div></div>
  </section>
  <section class="grid">
    <div class="panel chart-card"><div class="chart-title">Churn rate by contract</div><div class="chart-note">Month-to-month customers are the highest-risk contract group.</div><div id="contractChart"></div></div>
    <div class="panel chart-card"><div class="chart-title">Retention trend by tenure</div><div class="chart-note">Tenure-band view is used because the source has no calendar date.</div><div id="tenureChart"></div></div>
    <div class="panel chart-card"><div class="chart-title">Revenue at risk by internet service</div><div class="chart-note">Prioritizes segments by recurring revenue exposure.</div><div id="internetChart"></div></div>
    <div class="panel chart-card"><div class="chart-title">Churn rate by payment method</div><div class="chart-note">Payment-friction signal for retention campaigns.</div><div id="paymentChart"></div></div>
    <div class="panel insights full">
      <h2>Decision cues</h2>
      <p><strong>Retention:</strong> Focus the first-year journey and contract-conversion motion on month-to-month customers.</p>
      <p><strong>Revenue:</strong> Combine churn rate with monthly revenue at risk so campaigns prioritize economic value, not just volume.</p>
      <p><strong>Measurement:</strong> Refresh the dashboard with dated subscription or billing snapshots to unlock true monthly cohort and month-over-month analysis.</p>
    </div>
  </section>
  <div class="footer">Source: IBM Telco Customer Churn sample. Estimated CLV is observed TotalCharges, not a predictive CLV model. Dashboard generated from source-controlled Python and SQLite outputs.</div>
</div>
<script>
const records = {payload};
const dimensions = {{
  contract: [...new Set(records.map(r => r.contract))].sort(),
  internet: [...new Set(records.map(r => r.internet_service))].sort(),
  payment: [...new Set(records.map(r => r.payment_method))].sort(),
  tenure: ['0-12 months','13-24 months','25-48 months','49+ months']
}};
for (const [id, values] of Object.entries(dimensions)) {{ const el=document.getElementById(id); values.forEach(v => {{ const o=document.createElement('option'); o.textContent=v; el.appendChild(o); }}); }}
const money = x => '$' + Math.round(x).toLocaleString('en-US');
const pct = x => (x*100).toFixed(1) + '%';
const filtered = () => records.filter(r => (document.getElementById('contract').value==='All'||r.contract===document.getElementById('contract').value) && (document.getElementById('internet').value==='All'||r.internet_service===document.getElementById('internet').value) && (document.getElementById('payment').value==='All'||r.payment_method===document.getElementById('payment').value) && (document.getElementById('tenure').value==='All'||r.tenure_band===document.getElementById('tenure').value));
function grouped(data, key) {{ const map={{}}; data.forEach(r=>{{ const k=r[key]; if(!map[k]) map[k]={{n:0,churn:0,retained:0,revenue:0,risk:0}}; map[k].n++; map[k].churn+=r.churn_flag; map[k].retained+=r.retained_flag; map[k].revenue+=r.monthly_charges; map[k].risk+=r.monthly_revenue_at_risk; }}); return map; }}
function bar(target, labels, values, color, axisTitle) {{ Plotly.react(target,[{{x:values,y:labels,type:'bar',orientation:'h',marker:{{color}},hovertemplate:'%{{y}}<br>%{{x:.1f}}<extra></extra>'}}],{{margin:{{l:135,r:22,t:12,b:42}},height:290,paper_bgcolor:'transparent',plot_bgcolor:'transparent',xaxis:{{title:axisTitle,gridcolor:'#e6eef5'}},yaxis:{{automargin:true}},font:{{family:'Inter,system-ui,sans-serif',color:'#243b53'}}}},{{displayModeBar:false,responsive:true}}); }}
function update() {{
 const data=filtered(), n=data.length, churn=data.reduce((s,r)=>s+r.churn_flag,0), retained=data.reduce((s,r)=>s+r.retained_flag,0), revenue=data.reduce((s,r)=>s+r.monthly_charges,0), risk=data.reduce((s,r)=>s+r.monthly_revenue_at_risk,0), clv=data.reduce((s,r)=>s+r.estimated_clv,0);
 document.getElementById('kpiCustomers').textContent=n.toLocaleString('en-US'); document.getElementById('kpiChurn').textContent=n?pct(churn/n):'—'; document.getElementById('kpiRevenue').textContent=money(revenue); document.getElementById('kpiRisk').textContent=money(risk); document.getElementById('kpiClv').textContent=money(n?clv/n:0);
 let g=grouped(data,'contract'), keys=Object.keys(g).sort((a,b)=>g[b].churn/g[b].n-g[a].churn/g[a].n); bar('contractChart',keys,keys.map(k=>100*g[k].churn/g[k].n),'#e45756','Churn rate (%)');
 g=grouped(data,'tenure_band'); keys=['0-12 months','13-24 months','25-48 months','49+ months'].filter(k=>g[k]); bar('tenureChart',keys,keys.map(k=>100*g[k].retained/g[k].n),'#2a9d8f','Retention rate (%)');
 g=grouped(data,'internet_service'); keys=Object.keys(g).sort((a,b)=>g[b].risk-g[a].risk); bar('internetChart',keys,keys.map(k=>g[k].risk),'#f4a261','Revenue at risk ($)');
 g=grouped(data,'payment_method'); keys=Object.keys(g).sort((a,b)=>g[b].churn/g[b].n-g[a].churn/g[a].n); bar('paymentChart',keys,keys.map(k=>100*g[k].churn/g[k].n),'#264653','Churn rate (%)');
}}
['contract','internet','payment','tenure'].forEach(id=>document.getElementById(id).addEventListener('change',update)); update();
</script>
</body>
</html>'''
OUT_PATH.write_text(page)
print({'dashboard': str(OUT_PATH), 'records_embedded': len(records), 'bytes': OUT_PATH.stat().st_size})
