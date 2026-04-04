import sys
import os
sys.path.append(os.getcwd())
import json
import psycopg2
import requests
from decimal import Decimal
from datetime import datetime, date

SRC_HOST = "34.39.132.36"
SRC_PORT = 5432
SRC_DB   = "agente_financiero_db"
SRC_USER = "postgres"
SRC_PASS = "FinancialAgent_2026!"
SUPABASE_URL     = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

def supabase_headers(prefer_upsert=True):
    h = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": "Bearer " + SUPABASE_API_KEY,
        "Content-Type": "application/json",
    }
    if prefer_upsert:
        h["Prefer"] = "resolution=ignore-duplicates,return=minimal"
    return h

def serialize_row(row_dict):
    result = {}
    for k, v in row_dict.items():
        if isinstance(v, datetime):
            result[k] = v.isoformat()
        elif isinstance(v, date):
            result[k] = v.isoformat()
        elif isinstance(v, Decimal):
            result[k] = float(v)
        else:
            result[k] = v
    return result

def main():
    conn = psycopg2.connect(host=SRC_HOST, port=SRC_PORT, dbname=SRC_DB, user=SRC_USER, password=SRC_PASS, connect_timeout=15)
    with conn.cursor() as cur:
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='transactions' ORDER BY ordinal_position;")
        cols = [r[0] for r in cur.fetchall()]
        cols_sql = ", ".join(f'"{c}"' for c in cols)
        cur.execute(f"SELECT {cols_sql} FROM public.transactions WHERE type = 'INCOME' AND transaction_date >= '2026-01-01' LIMIT 1;")
        row = cur.fetchone()
    if row:
        payload = [serialize_row(dict(zip(cols, row)))]
        r = requests.post(f"{SUPABASE_URL}/rest/v1/transactions", headers=supabase_headers(), data=json.dumps(payload))
        print(r.status_code)
        import pprint
        pprint.pprint(r.json())

if __name__ == "__main__":
    main()
