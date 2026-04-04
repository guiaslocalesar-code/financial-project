import requests
import sys

SUPABASE_URL = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Prefer": "count=exact"
}

tables = [
    "companies","clients","services","client_services",
    "invoices","invoice_items","expense_types","expense_categories",
    "expense_budgets","income_budgets","transactions",
    "users","user_companies","payment_methods",
    "debts","debt_installments",
    "commission_recipients","commission_rules","commissions"
]

print("Checking Supabase tables...")
print("=" * 60)

for table in tables:
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table}?select=id&limit=0",
            headers=headers,
            timeout=8
        )
        if r.status_code == 200:
            cr = r.headers.get("content-range", "?")
            print(f"  OK  {table:<25} rows: {cr}")
        elif r.status_code == 404:
            print(f"  MISS {table:<25} NOT FOUND (404)")
        else:
            print(f"  ERR {table:<25} HTTP {r.status_code}: {r.text[:80]}")
    except requests.exceptions.Timeout:
        print(f"  TIMEOUT {table}")
    except Exception as e:
        print(f"  ERR {table:<25} {str(e)[:80]}")
    sys.stdout.flush()

print("\nDone.")
