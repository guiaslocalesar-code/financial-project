import requests

SUPABASE_URL     = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

def supabase_headers():
    return {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}"
    }

def check_table():
    url = f"{SUPABASE_URL}/rest/v1/transactions?limit=1"
    r = requests.get(url, headers=supabase_headers())
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    check_table()
