import requests
import json

SUPABASE_URL     = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

def supabase_headers():
    return {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json"
    }

def test_rpc():
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    payload = {"sql": "SELECT 1"}
    r = requests.post(url, headers=supabase_headers(), data=json.dumps(payload))
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    test_rpc()
