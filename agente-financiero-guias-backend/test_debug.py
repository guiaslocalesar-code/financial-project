import urllib.request
import urllib.error
import json

# Query the debug endpoint to get actual DB columns
url = "https://finanzas.guiaslocales.com.ar/finance-api/users/companies/aeb56588-5e15-4ce2-b24b-065ebf842c44"

payload = {
  "email": "limboxviajesyturismo@gmail.com",
  "role": "owner",
  "permissions": ["invoices:read", "debts:write"],
  "quotaparte": 50
}

req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("SUCCESS:")
        print(json.dumps(data, indent=2, default=str))
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTP {e.code}:")
    try:
        data = json.loads(body)
        print(json.dumps(data, indent=2, default=str))
    except:
        print(body)
