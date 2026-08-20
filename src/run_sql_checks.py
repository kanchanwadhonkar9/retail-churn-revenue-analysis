from pathlib import Path
import json
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / 'data' / 'cleaned' / 'retail_churn.sqlite'
SQL_PATH = ROOT / 'sql' / 'business_questions.sql'
OUT_PATH = ROOT / 'reports' / 'sql_validation.json'

sql_text = SQL_PATH.read_text()
queries = re.split(r'(?=-- Q\d{2}\.)', sql_text)
results = []
with sqlite3.connect(DB_PATH) as conn:
    conn.row_factory = sqlite3.Row
    for block in queries:
        block = block.strip()
        if not block or not block.startswith('-- Q'):
            continue
        match = re.match(r'-- (Q\d{2})\. ([^\n]+)', block)
        query_id, question = match.groups()
        sql = block[block.find('\n') + 1:].strip()
        rows = [dict(row) for row in conn.execute(sql).fetchall()]
        results.append({'query_id': query_id, 'question': question, 'rows_returned': len(rows), 'sample': rows[:3]})

OUT_PATH.write_text(json.dumps(results, indent=2, default=str))
print(json.dumps({'queries_validated': len(results), 'zero_row_queries': [r['query_id'] for r in results if r['rows_returned'] == 0]}, indent=2))
