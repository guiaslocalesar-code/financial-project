import asyncio
import asyncpg
from app.config import settings

async def full_audit():
    # Try different ports if 5432 fails
    ports = [5432, 6543]
    url_base = settings.async_database_url
    
    print(f"Starting full audit. Base URL: {url_base}")
    
    # Extract host, user, pass from URL
    # Format: postgresql+asyncpg://user:pass@host:port/dbname
    try:
        parts = url_base.split("://")[1].split("@")
        user_pass = parts[0].split(":")
        user = user_pass[0]
        password = user_pass[1].replace("%40", "@")
        host_port_db = parts[1].split("/")
        host_port = host_port_db[0].split(":")
        host = host_port[0]
        # port = int(host_port[1])
        db_name = host_port_db[1]
    except Exception as e:
        print(f"Failed to parse URL: {e}")
        return

    for port in ports:
        print(f"\n--- Testing Port {port} ---")
        try:
            conn = await asyncio.wait_for(
                asyncpg.connect(user=user, password=password, database=db_name, host=host, port=port),
                timeout=10
            )
            print("Connected!")
            
            # List all tables and their columns
            rows = await conn.fetch("""
                SELECT table_name, column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                ORDER BY table_name, ordinal_position
            """)
            
            current_table = None
            for row in rows:
                if row['table_name'] != current_table:
                    current_table = row['table_name']
                    print(f"\nTable: {current_table}")
                print(f"  - {row['column_name']} ({row['data_type']})")
                
            await conn.close()
            break # Exit loop if successful
        except asyncio.TimeoutError:
            print(f"Timeout on port {port}")
        except Exception as e:
            print(f"Error on port {port}: {e}")

if __name__ == "__main__":
    asyncio.run(full_audit())
