import psycopg2
try:
    conn = psycopg2.connect(
        host="aws-0-sa-east-1.pooler.supabase.com", port=6543, dbname="postgres",
        user="postgres.fumejzkghviszmyfjegg", password="GuiasSA2020@", connect_timeout=15,
        sslmode="require"
    )
    print("SUCCESS")
    conn.close()
except Exception as e:
    print(f"FAIL: {e}")
