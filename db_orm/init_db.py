from dotenv import load_dotenv
load_dotenv()

import asyncio
from db_orm.db import engine
from api_fastapi.db.models import Base, ApiBenchmarkLog,   # ✅ Import it explicitly!
from benchmaker.db.models import Base, Benchmark

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Optional: start fresh
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_models())
