# benchmaker/db/db_handlers.py

from sqlalchemy.ext.asyncio import AsyncSession
from benchmaker.db.bench_models import Benchmark
from datetime import datetime


async def insert_benchmark_record(
    db: AsyncSession,
    endpoint: str,
    method: str,
    url: str,
    input: dict | None,
    status: int,
    name: str | None,
    key: str | None,
    operation: str | None,
    sources: list[str] | None,
    result: dict | None,
    elapsed: float,
):
    record = Benchmark(
        endpoint=endpoint,
        method=method,
        url=url,
        input=input,
        status=status,
        name=name,
        key=key,
        operation=operation,
        sources=sources,
        result=result,
        elapsed=elapsed,
        timestamp=datetime.utcnow(),
    )
    db.add(record)
    await db.commit()
