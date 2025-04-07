import time
from functools import wraps
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from db_orm.db import get_db
from api_fastapi.db.models import ApiBenchmarkLog
from datetime import datetime
import inspect


def benchmark_endpoint(endpoint_name: str):
    def decorator(func):
        sig = inspect.signature(func)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            db: AsyncSession = kwargs.get("db")

            # Auto-inject default placeholders if not passed
            if "request" in sig.parameters and "request" not in kwargs:
                kwargs["request"] = request = None
            if "db" in sig.parameters and "db" not in kwargs:
                kwargs["db"] = db = None

            start = time.perf_counter()

            try:
                result = await func(*args, **kwargs)
                elapsed = time.perf_counter() - start

                # Determine HTTP status code
                if isinstance(result, Response):
                    status_code = result.status_code
                else:
                    status_code = 200  # default fallback

                if db:
                    log = ApiBenchmarkLog(
                        endpoint=endpoint_name or (request.url.path if request else "UNKNOWN"),
                        method=request.method if request else "UNKNOWN",
                        status=status_code,
                        name=kwargs.get("name"),
                        key=kwargs.get("key"),
                        operation=kwargs.get("operation"),
                        sources=kwargs.get("sources"),
                        result=result,
                        elapsed=elapsed,
                        timestamp=datetime.utcnow()
                    )
                    db.add(log)
                    await db.commit()

                print(f"✅ {endpoint_name} responded {status_code} in {elapsed:.4f}s")
                return result

            except Exception as e:
                elapsed = time.perf_counter() - start

                print(f"❌ {endpoint_name} failed after {elapsed:.4f}s: {e}")

                if db:
                    error_log = ApiBenchmarkLog(
                        endpoint=endpoint_name or (request.url.path if request else "UNKNOWN"),
                        method=request.method if request else "UNKNOWN",
                        status=500,
                        name=kwargs.get("name"),
                        key=kwargs.get("key"),
                        operation=kwargs.get("operation"),
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
