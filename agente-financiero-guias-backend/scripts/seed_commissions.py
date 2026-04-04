"""
Script de datos iniciales para el sistema de comisiones.
Crea 3 recipients y sus reglas de comisión.

Uso:
    python scripts/seed_commissions.py <company_id>

Ejemplo:
    python scripts/seed_commissions.py aeb56588-5e15-4ce2-b24b-065ebf842c44
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path para importar app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.commission_recipient import CommissionRecipient
from app.models.commission_rule import CommissionRule
from app.utils.enums import RecipientType

SEED_DATA = [
    {
        "recipient": {
            "type": RecipientType.SUPPLIER,
            "name": "Guias 2.0",
            "cuit": None,
            "email": None,
        },
        "rule": {
            "client_id": None,
            "service_id": "45413",   # Meta
            "percentage": 25.0,
            "priority": 1,
        }
    },
    {
        "recipient": {
            "type": RecipientType.EMPLOYEE,
            "name": "Juan Pérez",
            "cuit": None,
            "email": None,
        },
        "rule": {
            "client_id": None,
            "service_id": "45311",   # Google Ads
            "percentage": 15.0,
            "priority": 1,
        }
    },
    {
        "recipient": {
            "type": RecipientType.PARTNER,
            "name": "Agencia X",
            "cuit": None,
            "email": None,
        },
        "rule": {
            "client_id": None,
            "service_id": "45612",   # TikTok
            "percentage": 20.0,
            "priority": 1,
        }
    },
]


async def seed(company_id: str):
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        for entry in SEED_DATA:
            # Crear recipient
            rec = CommissionRecipient(
                company_id=company_id,
                **entry["recipient"]
            )
            db.add(rec)
            await db.flush()

            # Crear rule
            rule = CommissionRule(
                company_id=company_id,
                recipient_id=rec.id,
                **entry["rule"]
            )
            db.add(rule)
            print(f"  ✓ {entry['recipient']['name']} ({entry['recipient']['type']}) "
                  f"→ servicio {entry['rule']['service_id']} → {entry['rule']['percentage']}%")

        await db.commit()
        print("\n✅ Seed de comisiones completado.")

    await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/seed_commissions.py <company_id>")
        sys.exit(1)
    asyncio.run(seed(sys.argv[1]))
