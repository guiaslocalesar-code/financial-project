
import os

path = r'c:\Users\lea32\Finanzas-Guias\agente-financiero-guias-backend\live_db_summary.txt'
if os.path.exists(path):
    with open(path, 'rb') as f:
        content = f.read().decode('utf-16')
        print(content)
else:
    print("File not found")
