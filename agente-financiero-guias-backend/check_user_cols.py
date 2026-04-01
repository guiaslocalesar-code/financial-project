import asyncio
import ssl
import urllib.request
import json
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

async def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    engine = create_async_engine(settings.async_database_url, connect_args={"ssl": ctx})
    
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"))
        cols = [r[0] for r in res]
        print("Users table:", cols)
        
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'user_companies'"))
        cols = [r[0] for r in res]
        print("UserCompanies table:", cols)

if __name__ == "__main__":
    asyncio.run(main())
