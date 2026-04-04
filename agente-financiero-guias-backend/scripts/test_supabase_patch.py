import requests
import json

SUPABASE_URL     = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

def supabase_headers():
    return {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation" # Let's see what it returns
    }

def update_test():
    url = f"{SUPABASE_URL}/rest/v1/transactions?limit=1"
    # Get one record first to find an ID
    r_get = requests.get(url, headers=supabase_headers())
    if r_get.status_code != 200 or not r_get.json():
        print("Could not find a transaction to test.")
        return
    
    tid = r_get.json()[0]['id']
    print(f"Testing update on transaction {tid}...")
    
    update_url = f"{SUPABASE_URL}/rest/v1/transactions?id=eq.{tid}"
    payload = {
        "payment_method": "transfer",
        "payment_method_id": "pm_transferencia"
    }
    
    r_patch = requests.patch(update_url, headers=supabase_headers(), data=json.dumps(payload))
    print(f"PATCH Status: {r_patch.status_code}")
    print(f"PATCH Response: {r_patch.text}")

if __name__ == "__main__":
    update_test()
