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
    
    payload = {
        "payment_method": "transfer"
    }
    
    print("Updating Supabase transactions (payment_method only) + ID filter...")
    r = requests.patch(url, headers=supabase_headers(), data=json.dumps(payload))
    
    if r.status_code in (200, 201, 204):
        print("Supabase: Transactions updated (payment_method).")
    else:
        print(f"Supabase ERROR: HTTP {r.status_code} - {r.text}")
        if "invalid input value for enum" in r.text or "42704" in r.text: # 42704 is undefined_object
            print("Trying with UPPERCASE 'TRANSFER'...")
            payload["payment_method"] = "TRANSFER"
            r2 = requests.patch(url, headers=supabase_headers(), data=json.dumps(payload))
            if r2.status_code in (200, 201, 204):
                print("Supabase: Transactions updated with 'TRANSFER'.")
            else:
                print(f"Failed again: {r2.text}")

if __name__ == "__main__":
    update_supabase_filtered()
