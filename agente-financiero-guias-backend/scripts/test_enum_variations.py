import requests
import json

SUPABASE_URL     = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

def supabase_headers():
    return {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

def update_supabase_filtered():
    url = f"{SUPABASE_URL}/rest/v1/transactions?id=not.is.null"
    
    # Try common variations
    variations = ["transfer", "TRANSFER", "Transferencia", "transferencia"]
    
    for val in variations:
        print(f"Trying variation: '{val}'...")
        payload = {"payment_method": val}
        r = requests.patch(url, headers=supabase_headers(), data=json.dumps(payload))
        if r.status_code in (200, 201, 204):
            print(f"SUCCESS with '{val}'!")
            return
        else:
            print(f"FAIL: {r.status_code} - {r.text}")

if __name__ == "__main__":
    update_supabase_filtered()
