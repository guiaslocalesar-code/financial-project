import requests
import json
from scripts.migrar_supabase_rest import connect_src, get_columns_src, serialize_row, SUPABASE_URL, supabase_headers

def find():
    src_conn = connect_src()
    tabla = "commission_recipients"
    columnas = get_columns_src(src_conn, tabla)
    
    with src_conn.cursor() as cur:
        cur.execute(f"SELECT * FROM public.{tabla} LIMIT 1;")
        row = cur.fetchone()
    
    if not row:
        print("No data in Cloud SQL to test.")
        return

    base_payload = serialize_row(dict(zip(columnas, row)))
    
    # Pruebas
    tests = ["SUPPLIER", "supplier", "Supplier", "PROVEEDOR", "proveedor", "Proveedor", "1", 1]
    
    for t in tests:
        payload = base_payload.copy()
        payload["type"] = t
        
        url = f"{SUPABASE_URL}/rest/v1/{tabla}"
        h = supabase_headers(prefer_upsert=True)
        
        print(f"Testing value: {t} ...", end=" ")
        r = requests.post(url, headers=h, json=[payload])
        if r.status_code in (200, 201):
            print("SUCCESS!")
            return
        else:
            print(f"FAILED ({r.status_code}) - {r.text}")

if __name__ == "__main__":
    find()
