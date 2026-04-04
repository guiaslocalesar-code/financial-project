import asyncio
import uuid
from app.database import SessionLocal
from app.models.commission import Commission

async def debug():
    async with SessionLocal() as db:
        comm_id = uuid.UUID("d4d7bb5f-bbcf-4d2f-ab26-15a2a3ab55f0")
        comm = await db.get(Commission, comm_id)
        if comm:
            print("Found!", comm.id, comm.status)
        else:
            print("Not found.")

if __name__ == "__main__":
    asyncio.run(debug())
