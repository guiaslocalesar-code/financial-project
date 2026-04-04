import requests
import json
from scripts.migrar_supabase_rest import connect_src, SUPABASE_URL, supabase_headers

ID_TO_DELETE = "f51c4121-98d6-498d-b37f-be3b5793f24a"

def delete_cloud_sql():
    print(f"--- Eliminando de Cloud SQL: {ID_TO_DELETE} ---")
    conn = connect_src()
    try:
        with conn.cursor() as cur:
            # 1. Eliminar comisiones si existen (cascada manual por si acaso)
            cur.execute("DELETE FROM commissions WHERE recipient_id = %s", (ID_TO_DELETE,))
            count_c = cur.rowcount
            
            # 2. Eliminar reglas
            cur.execute("DELETE FROM commission_rules WHERE recipient_id = %s", (ID_TO_DELETE,))
            count_r = cur.rowcount
            
            # 3. Eliminar destinatario
            cur.execute("DELETE FROM commission_recipients WHERE id = %s", (ID_TO_DELETE,))
            count_rec = cur.rowcount
            
            conn.commit()
            print(f"✅ Eliminado: {count_rec} destinatario, {count_r} reglas, {count_c} comisiones.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error en Cloud SQL: {e}")
    finally:
        conn.close()

def delete_supabase():
    print(f"--- Eliminando de Supabase: {ID_TO_DELETE} ---")
    
    # 1. Eliminar comisiones
    r_com = requests.delete(f"{SUPABASE_URL}/rest/v1/commissions?recipient_id=eq.{ID_TO_DELETE}", headers=supabase_headers(False))
    # 2. Eliminar reglas
    r_rules = requests.delete(f"{SUPABASE_URL}/rest/v1/commission_rules?recipient_id=eq.{ID_TO_DELETE}", headers=supabase_headers(False))
    # 3. Eliminar destinatario
    r_rec = requests.delete(f"{SUPABASE_URL}/rest/v1/commission_recipients?id=eq.{ID_TO_DELETE}", headers=supabase_headers(False))
    
    if r_rec.status_code in (200, 204):
        print(f"✅ Eliminado de Supabase correctamente (Status: {r_rec.status_code})")
    else:
        print(f"❌ Error en Supabase: {r_rec.status_code} - {r_rec.text}")

if __name__ == "__main__":
    delete_cloud_sql()
    delete_supabase()
