import asyncio
import pandas as pd
from sqlalchemy import select
from app.database import SessionLocal
from app.models import Client

async def main():
    df = pd.read_csv(
        'csvs_para_reemplazar_ids/FLUJO-DE-DINERO-NEW-manual-de-marca-finanzas-2.csv'
    )

    updated = 0
    skipped = 0
    not_found = 0

    async with SessionLocal() as db:
        for _, row in df.iterrows():
            client_id = str(row['ID_Empresa']).strip().lower()
            foto_url = str(row['foto_link_perfil']).strip()

            # Si no hay URL, saltar
            if not foto_url or foto_url == 'nan':
                skipped += 1
                continue

            # Buscar cliente por ID
            result = await db.execute(select(Client).filter(Client.id == client_id))
            client = result.scalar_one_or_none()

            if not client:
                print(f"SKIP: client_id '{client_id}' no encontrado en DB")
                not_found += 1
                continue

            # Actualizar solo si imagen está vacía o es diferente
            if client.imagen != foto_url:
                client.imagen = foto_url
                updated += 1

        await db.commit()

    print(f"\n✅ Completado:")
    print(f"   Actualizados: {updated}")
    print(f"   Sin URL (skip): {skipped}")
    print(f"   No encontrados en DB: {not_found}")

if __name__ == "__main__":
    asyncio.run(main())
