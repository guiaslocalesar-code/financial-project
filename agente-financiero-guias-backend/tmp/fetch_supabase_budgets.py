import requests

SUPABASE_URL = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": "Bearer " + SUPABASE_API_KEY,
    "Content-Type": "application/json"
}

def fetch_all(table, select="*"):
    results = []
    offset = 0
    limit = 1000
    while True:
        url = f"{SUPABASE_URL}/rest/v1/{table}?select={select}&offset={offset}&limit={limit}"
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        results.extend(data)
        if len(data) < limit:
            break
        offset += limit
    return results

def main():
    clients_data = fetch_all("clients", "id,name")
    clients = {c['id']: c['name'] for c in clients_data}
    
    services_data = fetch_all("services", "id,name")
    services = {s['id']: s['name'] for s in services_data}
    
    budgets_data = fetch_all("income_budgets", "client_id,service_id,budgeted_amount,period_year,period_month")
    
    latest_budgets = {}
    for b in budgets_data:
        c_id = b['client_id']
        s_id = b['service_id']
        key = (c_id, s_id)
        if key not in latest_budgets:
            latest_budgets[key] = b
        else:
            curr = latest_budgets[key]
            if (b['period_year'] > curr['period_year']) or \
               (b['period_year'] == curr['period_year'] and b['period_month'] > curr['period_month']):
                latest_budgets[key] = b

    results = []
    for (c_id, s_id), b in latest_budgets.items():
        if c_id in clients and s_id in services:
            results.append({
                "client_name": clients[c_id],
                "service_name": services[s_id],
                "amount": b['budgeted_amount'],
                "period": f"{b['period_month']}/{b['period_year']}"
            })

    results.sort(key=lambda x: (x["client_name"], x["service_name"]))

    print(f"Total clientes: {len(clients_data)}")
    print(f"Total servicios: {len(services_data)}")
    print(f"Total presupuestos: {len(budgets_data)}")
    print("")
    print("| Cliente | Servicio | Monto | Periodo |")
    print("| :--- | :--- | :--- | :--- |")
    for r in results:
        # Formatear el monto con separador de miles si es posible
        try:
            monto = float(r['amount'])
            monto_str = f"{monto:,.2f}"
        except:
            monto_str = str(r['amount'])
        print(f"| {r['client_name']} | {r['service_name']} | {monto_str} | {r['period']} |")

if __name__ == "__main__":
    main()
