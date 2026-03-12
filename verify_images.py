import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def verify():
    async with SessionLocal() as db:
        # Query 1
        query1 = text("""
            SELECT 
              COUNT(*) as total_clients,
              COUNT(imagen) as con_imagen,
              COUNT(*) - COUNT(imagen) as sin_imagen
            FROM clients;
        """)
        result1 = await db.execute(query1)
        row1 = result1.fetchone()
        print(f"Total clientes: {row1[0]}")
        print(f"Con imagen: {row1[1]}")
        print(f"Sin imagen: {row1[2]}")

        print("\n--- Muestra de URLs ---")
        # Query 2
        query2 = text("""
            SELECT id, name, imagen 
            FROM clients 
            WHERE imagen IS NOT NULL
            LIMIT 10;
        """)
        result2 = await db.execute(query2)
        rows2 = result2.fetchall()
        for row in rows2:
            print(f"ID: {row[0]}, Name: {row[1]}, Imagen: {row[2][:50]}...")

        # Query 3
        query3 = text("SELECT id, name, imagen FROM clients WHERE id='c36'")
        result3 = await db.execute(query3)
        row3 = result3.fetchone()
        if row3:
            print(f"\nCheck c36: ID: {row3[0]}, Name: {row3[1]}, Imagen: {row3[2][:50] if row3[2] else 'None'}...")
        else:
            print("\nCheck c36: NOT FOUND")

if __name__ == "__main__":
    asyncio.run(verify())
