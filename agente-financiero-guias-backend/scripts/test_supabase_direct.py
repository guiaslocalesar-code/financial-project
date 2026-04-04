import psycopg2

DEST_HOST = "db.fumejzkghviszmyfjegg.supabase.co"
DEST_PORT = 5432
DEST_DB   = "postgres"
DEST_USER = "postgres"
DEST_PASS = "GuiasSA2020@"

def test_direct():
    try:
        conn = psycopg2.connect(
            host=DEST_HOST, port=DEST_PORT, dbname=DEST_DB,
            user=DEST_USER, password=DEST_PASS, connect_timeout=15,
            sslmode="require"
        )
        print("SUCCESS: Connected to Supabase directly via TCP.")
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            print(f"Version: {cur.fetchone()[0]}")
            
            # Also check if the column exists
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'transactions' AND column_name = 'payment_method_id';
            """)
            col = cur.fetchone()
            if col:
                print("Column payment_method_id EXISTS.")
            else:
                print("Column payment_method_id MISSING.")
        conn.close()
    except Exception as e:
        print(f"FAIL: {e}")

if __name__ == "__main__":
    test_direct()
