import requests
import json

# CONFIGURACIÓN (de scripts previos)
SUPABASE_URL     = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

def supabase_headers():
    return {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

def update_supabase():
    url = f"{SUPABASE_URL}/rest/v1/transactions"
    
    # Payload for PATCH: update all matching rows
    # In PostgREST, a PATCH update applies to all rows unless a filter is provided.
    # We want to update all transactions.
    
    payload = {
        "payment_method": "transfer",
        "payment_method_id": "pm_transferencia"
    }
    
    # We will execute the PATCH request. 
    # Caution: without filters, it will update EVERY row in the transactions table.
    
    print("Updating Supabase transactions...")
    r = requests.patch(url, headers=supabase_headers(), data=json.dumps(payload))
    
    if r.status_code in (200, 201, 204):
        print("Supabase: All transactions updated successfully.")
    else:
        print(f"Supabase ERROR: HTTP {r.status_code} - {r.text}")

if __name__ == "__main__":
    update_supabase()
