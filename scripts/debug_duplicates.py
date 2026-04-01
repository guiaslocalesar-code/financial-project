from scripts.migrar_supabase_rest import connect_src

def check():
    conn = connect_src()
    with conn.cursor() as cur:
        # 1. Buscar destinatarios con nombre similar
        cur.execute("SELECT id, name, type, created_at FROM commission_recipients WHERE name ILIKE '%Guias%';")
        recipients = cur.fetchall()
        print("\n=== Destinatarios Guias ===")
        for r in recipients:
            print(f"ID: {r[0]} | Name: {r[1]} | Type: {r[2]} | Created: {r[3]}")
            
            # Ver dependencias
            cur.execute("SELECT COUNT(*) FROM commission_rules WHERE recipient_id = %s", (r[0],))
            rules = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM commissions WHERE recipient_id = %s", (r[0],))
            commis = cur.fetchone()[0]
            print(f"   -> Reglas: {rules} | Comisiones: {commis}")
            
    conn.close()

if __name__ == "__main__":
    check()
