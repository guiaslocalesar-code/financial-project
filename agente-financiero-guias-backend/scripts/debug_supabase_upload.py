import sys
import json
import requests
from scripts.migrar_supabase_rest import connect_src, get_columns_src, serialize_row, SUPABASE_URL, supabase_headers

def debug():
    src_conn = connect_src()
    tabla = "commission_recipients"
    columnas = get_columns_src(src_conn, tabla)
    cols_sql = ", ".join('"%s"' % c for c in columnas)
    
    with src_conn.cursor() as cur:
        cur.execute(f"SELECT {cols_sql} FROM public.{tabla} LIMIT 2;")
        rows = cur.fetchall()
        
    payload = [serialize_row(dict(zip(columnas, row))) for row in rows]
    # Forzar la ausencia de 'type' para ver que error da
    for p in payload:
        if "type" in p:
            p.pop("type")
    
    url = f"{SUPABASE_URL}/rest/v1/{tabla}"
    h = supabase_headers(prefer_upsert=True)
    
    print("Sending payload:")
    print(json.dumps(payload, indent=2))
    
    r = requests.post(url, headers=h, data=json.dumps(payload))
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    debug()
