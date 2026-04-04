import requests
import pandas as pd

SUPABASE_URL = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": "Bearer " + SUPABASE_API_KEY,
    "Content-Type": "application/json",
}

def fetch_table(table_name):
    # Fetch all records using PostgREST pagination if necessary
    # Assuming < 1000 records, a single call is usually enough, but let's be safe.
    response = requests.get(f"{SUPABASE_URL}/rest/v1/{table_name}?select=*", headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    try:
        # We can try to fetch them joined first for efficiency
        # select=monthly_fee,status,clients(name),services(name)
        joined_query = f"{SUPABASE_URL}/rest/v1/client_services?select=monthly_fee,status,clients(name),services(name)"
        response = requests.get(joined_query, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            rows = []
            for item in data:
                cliente_name = item.get('clients', {}).get('name') if item.get('clients') else None
                servicio_name = item.get('services', {}).get('name') if item.get('services') else None
                rows.append({
                    'CLIENTE': cliente_name,
                    'SERVICIO': servicio_name,
                    'COSTO': item.get('monthly_fee'),
                    'ESTADO': item.get('status')
                })
            
            df = pd.DataFrame(rows)
            # Sort and remove any row that failed to join properly
            df = df.dropna(subset=['CLIENTE', 'SERVICIO'])
            df = df.sort_values(by=['CLIENTE', 'SERVICIO'])
            print(df.to_markdown(index=False))
            return
    except Exception as e:
        pass
    
    # Fallback to fetching entire tables and joining locally
    print("Fallback to local join")
    clients = fetch_table("clients")
    services = fetch_table("services")
    client_services = fetch_table("client_services")

    df_clients = pd.DataFrame(clients)[['id', 'name']].rename(columns={'id': 'client_id', 'name': 'CLIENTE'})
    df_services = pd.DataFrame(services)[['id', 'name']].rename(columns={'id': 'service_id', 'name': 'SERVICIO'})
    df_cs = pd.DataFrame(client_services)[['client_id', 'service_id', 'monthly_fee', 'status']]

    df = df_cs.merge(df_clients, on='client_id').merge(df_services, on='service_id')
    df = df.rename(columns={'monthly_fee': 'COSTO', 'status': 'ESTADO'})
    df = df[['CLIENTE', 'SERVICIO', 'COSTO', 'ESTADO']]
    df = df.sort_values(by=['CLIENTE', 'SERVICIO'])
    print(df.to_markdown(index=False))

if __name__ == "__main__":
    main()
