import asyncio
import uuid
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.user import User
from app.models.company import Company
from app.models.user_company import UserCompany
from app.config import settings
from app.utils.enums import CompanyRole

async def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    engine = create_async_engine(settings.async_database_url, connect_args={"ssl": ctx})
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as db:
        try:
            email = "matiasmazzucchini@gmail.com"
            user_res = await db.execute(select(User).where(User.email == email))
            user = user_res.scalar_one_or_none()
            print(f"User found: {user}")
            
            from app.schemas.user import UserCompanyInvite
            
            invite = UserCompanyInvite(
                email=email,
                role=CompanyRole.OWNER,
                permissions=['dashboard:read', 'clients:write'],
                quotaparte=50
            )
            print("Pydantic successfully validated:", invite)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
