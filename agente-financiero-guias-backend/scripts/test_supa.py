import sys
sys.path.append('.')
import json
import psycopg2
import requests
from datetime import datetime, date
from decimal import Decimal

# CONFIGURACIÓN
SRC_HOST = "34.39.132.36"
SRC_PORT = 5432
SRC_DB   = "agente_financiero_db"
SRC_USER = "postgres"
SRC_PASS = "FinancialAgent_2026!"

SUPABASE_URL     = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

def connect_src():
    return psycopg2.connect(
        host=SRC_HOST, port=SRC_PORT, dbname=SRC_DB,
        user=SRC_USER, password=SRC_PASS, connect_timeout=15
    )

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
    src = connect_src()
    with src.cursor() as cur:
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='income_budgets' ORDER BY ordinal_position;")
        columnas = [r[0] for r in cur.fetchall()]
        cols_sql = ", ".join(f'"{c}"' for c in columnas)
        cur.execute(f"SELECT {cols_sql} FROM public.income_budgets LIMIT 1;")
        row = cur.fetchone()
        
    payload = [serialize_row(dict(zip(columnas, row)))]
    url = f"{SUPABASE_URL}/rest/v1/income_budgets"
    print("SENDING TO", url)
    print("PAYLOAD:", json.dumps(payload, indent=2))
    
    r = requests.post(url, headers=supabase_headers(True), data=json.dumps(payload), timeout=60)
    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)

if __name__ == "__main__":
    main()
