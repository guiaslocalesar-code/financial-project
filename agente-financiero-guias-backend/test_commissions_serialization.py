import asyncio
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import SessionLocal
from app.main import app
from app.models.commission import CommissionRecipient, CommissionRule, Commission
from app.schemas.commission import CommissionRecipientResponse, CommissionResponse

async def main():
    company_id_str = "aeb56588-5e15-4ce2-b24b-065ebf842c44"
    print("Testing get recipients...")
    async with SessionLocal() as db:
        try:
            # Recipients
            query = select(CommissionRecipient).where(CommissionRecipient.company_id == company_id_str)
            res = await db.execute(query)
            recipients = res.scalars().all()
            print(f"Found {len(recipients)} recipients in DB")
            for r in recipients:
                try:
                    schema = CommissionRecipientResponse.model_validate(r)
                    # print(f"Recipient: {schema.name}")
                except Exception as e:
                    print(f"Validation error on recipient {r.id}: {e}")
            
            # Commissions
            query2 = select(Commission).join(CommissionRecipient, Commission.recipient_id == CommissionRecipient.id).where(CommissionRecipient.company_id == company_id_str)
            res2 = await db.execute(query2)
            commissions = res2.scalars().all()
            print(f"Found {len(commissions)} commissions in DB")
            for c in commissions:
                try:
                    schema = CommissionResponse.model_validate(c)
                except Exception as e:
                    print(f"Validation error on commission {c.id}: {e}")
                    
            # Rules
            from app.schemas.commission import CommissionRuleResponse
            from sqlalchemy.orm import joinedload
            query3 = (
                select(CommissionRule)
                .options(joinedload(CommissionRule.recipient), joinedload(CommissionRule.client), joinedload(CommissionRule.service))
                .join(CommissionRecipient, CommissionRule.recipient_id == CommissionRecipient.id)
                .where(CommissionRecipient.company_id == company_id_str)
            )
            res3 = await db.execute(query3)
            rules = res3.scalars().all()
            print(f"Found {len(rules)} rules in DB")
            for r in rules:
                # Manual enrichment like in router
                if r.recipient: setattr(r, "recipient_name", r.recipient.name)
                if r.client: setattr(r, "client_name", r.client.name)
                if r.service: setattr(r, "service_name", r.service.name)
                
                try:
                    schema = CommissionRuleResponse.model_validate(r)
                    print(f"Rule {r.id}: Recipient={schema.recipient_name}, Service={schema.service_name}, Client={schema.client_name}")
                except Exception as e:
                    print(f"Validation error on rule {r.id}: {e}")
                    
        except Exception as e:
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
