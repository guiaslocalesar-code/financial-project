import requests

SUPABASE_URL     = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

def supabase_headers():
    return {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}"
    }

def list_tables():
    url = f"{SUPABASE_URL}/rest/v1/"
    r = requests.get(url, headers=supabase_headers())
    print(f"Status Code: {r.status_code}")
    # This might be big! Let's check keys if it's JSON.
    if r.status_code == 200:
        try:
            data = r.json()
            if isinstance(data, dict):
                # Swagger spec! Look at paths.
                paths = data.get('paths', {})
                for path in paths:
                    if path.startswith('/'):
                        print(path)
            else:
                print(f"Data: {data}")
        except:
            print(f"Text: {r.text[:500]}")

if __name__ == "__main__":
    list_tables()
