import sqlalchemy as sa
from sqlalchemy import create_engine, text

# Sync connection string
# User: postgres.fumejzkghviszmyfjegg
# Pass: GuiasSA2020@
# Host: aws-1-us-east-1.pooler.supabase.com
# Port: 5432
# DB: postgres

URL = "postgresql://postgres.fumejzkghviszmyfjegg:GuiasSA2020%40@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

def check_db():
    print(f"Connecting to: {URL}")
    try:
        engine = create_engine(URL)
        with engine.connect() as conn:
            print("Connected successfully!")
            
            # Check transactions columns
            print("\nColumns in 'transactions' table:")
            res = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'transactions'"))
            for row in res:
                print(f"  - {row[0]}: {row[1]}")
            
            # Check if there are any rows
            print("\nRow count in 'transactions':")
            count = conn.execute(text("SELECT count(*) FROM transactions")).scalar()
            print(f"  Count: {count}")
            
            # Check enums
            print("\nDefined ENUM types:")
            res = conn.execute(text("SELECT t.typname FROM pg_type t JOIN pg_enum e ON t.oid = e.enumtypid GROUP BY t.typname"))
            for row in res:
                print(f"  - {row[0]}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
