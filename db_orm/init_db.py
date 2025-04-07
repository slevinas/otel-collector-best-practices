from dotenv import load_dotenv
load_dotenv()

import asyncio
from db_orm.db import engine
from db_orm.base import Base
from api_fastapi.db.models import  ApiBenchmarkLog ,StoredResource
from benchmaker.db.bench_models import  Benchmark

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Optional: start fresh
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_models())
