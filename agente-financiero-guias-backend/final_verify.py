import asyncio
import traceback
from sqlalchemy import select
from app.database import engine
from app.models.income_budget import IncomeBudget
from app.models.transaction import Transaction
from app.models.commission import Commission

async def check():
    print('Checking model mapping compatibility with DB...')
    async with engine.connect() as conn:
        for model in [IncomeBudget, Transaction, Commission]:
            try:
                print(f'Testing {model.__name__}...', end='', flush=True)
                res = await conn.execute(select(model).limit(1))
                data = res.all()
                print(f' OK (rows: {len(data)})')
            except Exception:
                print(' FAILED')
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check())
