"""
Script para ejecutar la migración de facturación e IVA en Supabase.
Usa la REST API con service_role key para ejecutar las queries.
"""
import requests
import json

SUPABASE_URL = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def check_column_exists(table, column):
    """Check if a column exists by trying to select it."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?select={column}&limit=1"
    r = requests.get(url, headers=headers)
    return r.status_code == 200

def add_columns_via_rpc():
    """
    Since we can't run raw DDL through the REST API with the anon key,
    we'll use PATCH to update records and verify the columns exist.
    First, let's check current state.
    """
    tables_to_check = {
        "clients": ["requires_invoice"],
        "income_budgets": ["requires_invoice", "iva_rate", "iva_amount"],
        "transactions": ["requires_invoice", "iva_rate", "iva_amount"],
    }
    
    print("=" * 60)
    print("VERIFICACIÓN DE COLUMNAS EN SUPABASE")
    print("=" * 60)
    
    all_exist = True
    for table, columns in tables_to_check.items():
        for col in columns:
            exists = check_column_exists(table, col)
            status = "✅ EXISTE" if exists else "❌ NO EXISTE"
            print(f"  {table}.{col}: {status}")
            if not exists:
                all_exist = False
    
    if all_exist:
        print("\n✅ Todas las columnas ya existen en la base de datos.")
        print("\nVerificando datos de Limbox...")
        verify_limbox()
        return True
    else:
        print("\n❌ Faltan columnas. Necesitás ejecutar el SQL manualmente.")
        print("   Abrí el SQL Editor de Supabase y ejecutá el contenido de:")
        print("   scripts/migration_requires_invoice_iva.sql")
        return False

def verify_limbox():
    """Verify Limbox client configuration."""
    url = f"{SUPABASE_URL}/rest/v1/clients?select=id,name,requires_invoice&name=ilike.*limbox*"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        clients = r.json()
        if clients:
            for c in clients:
                ri = c.get("requires_invoice", "N/A")
                print(f"  → {c['name']}: requires_invoice = {ri}")
                if ri is True:
                    print("    ⚠️  Limbox debería tener requires_invoice = false")
                    # Try to update
                    patch_url = f"{SUPABASE_URL}/rest/v1/clients?id=eq.{c['id']}"
                    patch_r = requests.patch(patch_url, headers=headers, json={"requires_invoice": False})
                    if patch_r.status_code in (200, 204):
                        print("    ✅ Actualizado a false")
                    else:
                        print(f"    ❌ No se pudo actualizar: {patch_r.status_code} {patch_r.text}")
        else:
            print("  No se encontró cliente Limbox")
    else:
        print(f"  Error: {r.status_code}")

def list_all_clients():
    """List all clients with their requires_invoice status."""
    url = f"{SUPABASE_URL}/rest/v1/clients?select=id,name,requires_invoice&order=name"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        clients = r.json()
        print(f"\n{'='*60}")
        print(f"CLIENTES ({len(clients)} total)")
        print(f"{'='*60}")
        for c in clients:
            ri = c.get("requires_invoice", "N/A")
            icon = "📄" if ri else "💰"
            label = "Blanco" if ri else "Negro"
            print(f"  {icon} {c['name']}: {label}")
    else:
        print(f"Error listando clientes: {r.status_code}")

if __name__ == "__main__":
    result = add_columns_via_rpc()
    if result:
        list_all_clients()
