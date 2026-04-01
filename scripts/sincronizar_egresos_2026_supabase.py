import sys
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

def get_columns_src(conn, tabla):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema='public' AND table_name=%s
            ORDER BY ordinal_position;
        """, (tabla,))
        return [r[0] for r in cur.fetchall()]

def migrar_tabla_condicional(src_conn, tabla, where_clause, delete_keys=None, only_keys=None):
    if delete_keys is None: delete_keys = []
    print(f"\n--- Migrando subconjunto de: {tabla} ---")
    
    columnas = get_columns_src(src_conn, tabla)
    cols_sql = ", ".join(f'"{c}"' for c in columnas)
    
    url = f"{SUPABASE_URL}/rest/v1/{tabla}"
    h = supabase_headers(prefer_upsert=True)
    
    # Check valid keys in Supabase
    r_sup = requests.get(f"{url}?limit=1", headers=supabase_headers(False))
    valid_keys = set()
    if r_sup.status_code == 200 and r_sup.json():
        valid_keys = set(r_sup.json()[0].keys())

    BATCH = 250
    insertados = 0
    errores = 0
    
    with src_conn.cursor(name=f"cur_{tabla}_2026") as cur:
        q = f"SELECT {cols_sql} FROM public.{tabla}"
        if where_clause:
            q += f" WHERE {where_clause}"
        if "created_at" in columnas:
            q += " ORDER BY created_at"
            
        cur.execute(q)
        
        while True:
            rows = cur.fetchmany(BATCH)
            if not rows:
                break
            
            payload = []
            for row in rows:
                d = serialize_row(dict(zip(columnas, row)))
                for k in delete_keys:
                    d.pop(k, None)
                if valid_keys:
                    d = {k: v for k, v in d.items() if k in valid_keys}
                if only_keys:
                    d = {k: v for k, v in d.items() if k in only_keys}
                payload.append(d)
                
            r = requests.post(url, headers=h, data=json.dumps(payload), timeout=60)
            
            if r.status_code in (200, 201):
                insertados += len(rows)
                print(f"  ... {insertados}", end="\r")
            else:
                errores += len(rows)
                print(f"\n  ERROR batch ({len(rows)} rows): HTTP {r.status_code} - {r.text}")
    
    print(f"\n  Nuevos/Upserts= {insertados} | Errores= {errores}")

def main():
    print("=" * 60)
    print("SINC DEL AÑO 2026 (EGRESOS): CLOUD SQL (GCP) -> SUPABASE via REST")
    print("=" * 60)
    
    src = connect_src()
    
    # 0. Migrar tipos y categorias de egresos
    migrar_tabla_condicional(src, "expense_types", "TRUE")
    migrar_tabla_condicional(src, "expense_categories", "TRUE")
    
    # 1. Migrar expense_budgets del 2026 SIN transaction_id para evitar FK violation
    migrar_tabla_condicional(src, "expense_budgets", "period_year >= 2026", delete_keys=['transaction_id'])
    
    # 2. Migrar transactions asociadas
    migrar_tabla_condicional(src, "transactions", "type = 'EXPENSE' AND transaction_date >= '2026-01-01'")
    
    # 3. Actualizar expense_budgets CON su transaction_id ahora que las transacciones existen
    migrar_tabla_condicional(src, "expense_budgets", "period_year >= 2026")
    
    src.close()
    print("\nTodo finalizado.")

if __name__ == "__main__":
    main()
