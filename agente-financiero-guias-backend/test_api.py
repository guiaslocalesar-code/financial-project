
import urllib.request
import json

try:
    with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/companies") as response:
        data = response.read().decode('utf-8')
        print("Success!")
        print(data)
except Exception as e:
    print(f"Error: {e}")
