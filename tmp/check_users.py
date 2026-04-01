import requests

SUPABASE_URL = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": "Bearer " + SUPABASE_API_KEY,
}

url = f"{SUPABASE_URL}/rest/v1/users?select=id&limit=1"
r = requests.get(url, headers=headers)
print(f"Users Status: {r.status_code}")
