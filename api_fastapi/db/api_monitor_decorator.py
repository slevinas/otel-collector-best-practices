import time
from functools import wraps
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from db_orm.db import get_db
from api_fastapi.db.models import ApiBenchmarkLog
from datetime import datetime
import inspect


def benchmark_endpoint(endpoint_name: str):
    def decorator(func):
        sig = inspect.signature(func)
        print(f"zigi from decorator the sig is {sig}")

        async def wrapper(*args, **kwargs):
            if "request" in sig.parameters and "request" not in kwargs:
                kwargs["request"] = None
            if "db" in sig.parameters and "db" not in kwargs:
                kwargs["db"] = None

            start = time.perf_counter()

            try:
                result = await func(*args, **kwargs)
                elapsed = time.perf_counter() - start

                if "db" in kwargs and kwargs["db"]:
                    db = kwargs["db"]
                    request = kwargs.get("request")

                    benchmark = ApiBenchmarkLog(
                        endpoint=endpoint_name,
                        method=request.method if request else "UNKNOWN",
                        status=200,
                        operation=kwargs.get("operation"),
                        key=kwargs.get("key"),
                        name=kwargs.get("name"),
                        sources=kwargs.get("sources"),
                        result=result,
                        elapsed=elapsed,
                        timestamp=datetime.utcnow()
                    )
                    db.add(benchmark)
                    await db.commit()

                print(f"✅ Endpoint `{endpoint_name}` completed in {elapsed:.4f}s")
                return result

            except Exception as e:
                elapsed = time.perf_counter() - start
                print(f"❌ Error in `{endpoint_name}` after {elapsed:.4f}s: {str(e)}")

                if "db" in kwargs and kwargs["db"]:
                    db = kwargs["db"]
                    request = kwargs.get("request")

                    error_log = ApiBenchmarkLog(
                        endpoint=endpoint_name,
                        method=request.method if request else "UNKNOWN",
                        status=500,
                        operation=kwargs.get("operation"),
                        key=kwargs.get("key"),
                        name=kwargs.get("name"),
                        sources=kwargs.get("sources"),
                        result={"error": str(e)},
                        elapsed=elapsed,
                        timestamp=datetime.utcnow()
                    )
                    db.add(error_log)
                    await db.commit()

                return JSONResponse(
                    status_code=500,
                    content={"detail": f"Internal error in {endpoint_name}: {str(e)}"}
                )

        return wrapper
    return decorator
