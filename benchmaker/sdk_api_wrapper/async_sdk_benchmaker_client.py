# json_key_reader_benchmaker_sdk.py
import httpx
import asyncio
from datetime import datetime
from benchmaker.db.db_handlers import insert_benchmark_record  # <- make sure this is your async insert logic
from db_orm.db import get_db
class JsonKeyReaderClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.token = None

    async def login(self):
        async with httpx.AsyncClient() as client:
            start = datetime.utcnow()
            url = f"{self.base_url}/login"
            data= {"username": self.username, "password": self.password}
            response = await client.post(
                url,
                data=data
            )
            elapsed = (datetime.utcnow() - start).total_seconds()
            response.raise_for_status()
            self.token = response.json()["access_token"]

            async for db in get_db():
                await insert_benchmark_record(
                    db=db,
                    endpoint="/login",
                    method="POST",
                    url=url,
                    input=data,
                    status=response.status_code,
                    name=None,
                    key=None,
                    operation=None,
                    sources=None,
                    result=response.json(),
                    elapsed=elapsed
                )

                return response.json()

    def _auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    async def store(self, name: str, data: dict):
        async with httpx.AsyncClient() as client:
            start = datetime.utcnow()
            url = f"{self.base_url}/store/{name}"
            response = await client.put(url, json=data, headers=self._auth_headers())
            elapsed = (datetime.utcnow() - start).total_seconds()
            response.raise_for_status()

        async for db in get_db():
            await insert_benchmark_record(
                db=db,
                endpoint="/store",
                method="PUT",
                url=url,
                input=data,
                status=response.status_code,
                name=name,
                key=None,
                operation=None,
                sources=None,
                result=response.json(),
                elapsed=elapsed
            )

            return response.json()

    async def run_math(self, operation: str, sources: list[str]):
        async with httpx.AsyncClient() as client:
            start = datetime.utcnow()
            payload = {"operation": operation, "sources": sources}
            url = f"{self.base_url}/run_vectorized_math"
            response = await client.post(url, json=payload, headers=self._auth_headers())
            elapsed = (datetime.utcnow() - start).total_seconds()
            response.raise_for_status()

            async for db in get_db():
                await insert_benchmark_record(
                    db=db,
                    endpoint="/run_vectorized_math",
                    method="POST",
                    url=url,
                    input=payload,
                    status=response.status_code,
                    name=None,
                    key=None,
                    operation=operation,
                    sources=sources,
                    result=response.json(),
                    elapsed=elapsed
                )

            return response.json()

    async def get_stored(self, name: str, key: str | None = None):
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/store/{name}"
            params = {"key": key} if key else {}
            start = datetime.utcnow()
            response = await client.get(url, headers=self._auth_headers(), params=params)
            elapsed = (datetime.utcnow() - start).total_seconds()
            response.raise_for_status()

            async for db in get_db():
                await insert_benchmark_record(
                    db=db,
                    endpoint="/store",
                    method="GET",
                    url=url,
                    input=None,
                    status=response.status_code,
                    name=name,
                    key=key,
                    operation=None,
                    sources=[name],
                    result=response.json(),
                    elapsed=elapsed
                )

            return response.json()
