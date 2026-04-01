import requests

SUPABASE_URL = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

def check():
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": "Bearer " + SUPABASE_API_KEY,
        "Content-Type": "application/json"
    }

    print("Verificando Supabase Tables...")
    tables = ["debt_installments", "commission_recipients", "commission_rules", "commissions"]
    
    for tabla in tables:
        url_count = f"{SUPABASE_URL}/rest/v1/{tabla}?select=id"
        h_count = headers.copy()
        h_count["Prefer"] = "count=exact"
        h_count["Range"] = "0-0"
        
        r1 = requests.get(url_count, headers=h_count)
        if r1.status_code in (200, 206):
            crange = r1.headers.get("Content-Range", "")
            print(f"Table {tabla:25}: {crange}")
        else:
            print(f"Table {tabla:25}: ERROR {r1.status_code}")

    # 2. Traer 5 comisiones
    url_data = f"{SUPABASE_URL}/rest/v1/commissions?select=id,client_id,commission_amount&limit=5"
    r2 = requests.get(url_data, headers=headers)
    if r2.status_code == 200:
        data = r2.json()
        print(f"\nObtenidas {len(data)} muestras:")
        for row in data:
            print(f"ID: {row['id']} | Client: {row['client_id']} | Amount: {row['commission_amount']}")
    else:
        print(f"Error obteniendo: {r2.status_code} {r2.text}")

if __name__ == "__main__":
    check()
