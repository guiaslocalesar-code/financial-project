import requests
import sys
import json

SUPABASE_URL = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
}

tables = [
    "companies","clients","services","client_services",
    "invoices","invoice_items","expense_types","expense_categories",
    "expense_budgets","income_budgets","transactions",
    "users","user_companies","payment_methods",
    "debts","debt_installments",
    "commission_recipients","commission_rules","commissions"
]

results = []

for table in tables:
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table}?select=*&limit=1",
            headers={**headers, "Prefer": "count=exact"},
            timeout=8
        )
        cr = r.headers.get("content-range", "?")
        data = r.json()
        
        if data and isinstance(data, list) and len(data) > 0:
            cols = sorted(data[0].keys())
        else:
            cols = []
        
        count = cr.split("/")[-1] if "/" in cr else "?"
        results.append({"table": table, "count": count, "columns": cols})
    except Exception as e:
        results.append({"table": table, "count": "ERR", "columns": [], "error": str(e)[:80]})

with open("tmp/supabase_tables.json", "w") as f:
    json.dump(results, f, indent=2)

print("Saved to tmp/supabase_tables.json")
