import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.commission_recipient import CommissionRecipient
from app.models.commission_rule import CommissionRule
from app.utils.enums import RecipientType

COMPANY_ID = "aeb56588-5e15-4ce2-b24b-065ebf842c44"

GUIAS_RULES = [
    {"service_id": "45311", "percentage": 24.0}, # Google Ads
    {"service_id": "45413", "percentage": 12.0}, # Meta
    {"service_id": "45612", "percentage": 12.0}, # Tik Tok
    {"service_id": "45892", "percentage": 24.0}, # Google Bsn
    {"service_id": "45897", "percentage": 100.0}, # Data
    {"service_id": "45900", "percentage": 12.0}, # Pagina Web Ecomerce
]

async def seed_guias():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # 1. Crear recipient
        recipient = CommissionRecipient(
            company_id=COMPANY_ID,
            type=RecipientType.SUPPLIER,
            name="Guias 2.0",
            is_active=True
        )
        db.add(recipient)
        await db.flush()
        
        print(f"✓ Recipient 'Guias 2.0' creado con ID: {recipient.id}")

        # 2. Crear reglas
        for r_data in GUIAS_RULES:
            rule = CommissionRule(
                company_id=COMPANY_ID,
                recipient_id=recipient.id,
                service_id=r_data["service_id"],
                percentage=r_data["percentage"],
                is_active=True
            )
            db.add(rule)
            print(f"  ✓ Regla: Servicio {r_data['service_id']} -> {r_data['percentage']}%")

        await db.commit()
        print("\n✅ Seed de Guias 2.0 completado.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_guias())
