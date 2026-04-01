import psycopg2

# Probar distintos host de pooler para encontrar la region correcta
# El proyecto puede estar en us-east-1, sa-east-1, eu-central-1, etc.
PROJECT_REF = "fumejzkghviszmyfjegg"
PASS = "GuiasSA2020@"

pooler_hosts = [
    "aws-0-sa-east-1.pooler.supabase.com",       # Brasil / SA
    "aws-0-us-east-1.pooler.supabase.com",        # US East
    "aws-0-us-west-1.pooler.supabase.com",        # US West
    "aws-0-eu-central-1.pooler.supabase.com",     # EU Frankfurt
    "aws-0-ap-southeast-1.pooler.supabase.com",   # Asia Pacific
]

for host in pooler_hosts:
    for port in [6543, 5432]:
        for user_fmt in [
            "postgres.%s" % PROJECT_REF,
            "postgres",
        ]:
            try:
                c = psycopg2.connect(
                    host=host, port=port, dbname="postgres",
                    user=user_fmt, password=PASS, connect_timeout=10, sslmode="require"
                )
                print("SUCCESS: host=%s port=%d user=%s version=%s" % (host, port, user_fmt, c.server_version))
                c.close()
            except Exception as e:
                err = str(e)[:80].replace("\n", " ")
                print("FAIL: host=%s port=%d user=%s err=%s" % (host, port, user_fmt, err))
