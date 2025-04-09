# cli.py
import asyncio
import typer
import json
from benchmaker.sdk_api_wrapper.async_sdk_benchmaker_client import JsonKeyReaderClient

app = typer.Typer()

BASE_URL = "http://127.0.0.1:8010"
USERNAME = "admin"
PASSWORD = "admin123"


@app.command()
def store(name: str, x: float, y: float):
    """Store a JSON object under a given name."""
    async def run():
        client = JsonKeyReaderClient(BASE_URL, USERNAME, PASSWORD)
        await client.login()
        payload = {"x": {"value": x}, "y": {"value": y}}
        result = await client.store(name, payload)
        print(json.dumps(result, indent=2))
    asyncio.run(run())


@app.command()
def get(name: str, key: str = typer.Option(None, help="Optional nested key like x.value")):
    """Retrieve a stored resource by name and optional nested key."""
    async def run():
        client = JsonKeyReaderClient(BASE_URL, USERNAME, PASSWORD)
        await client.login()
        result = await client.get_stored(name, key)
        print(json.dumps(result, indent=2))
    asyncio.run(run())


@app.command()
def run_math(operation: str, sources: list[str]):
    """Run vector math (add or subtract) on JSON sources."""
    async def run():
        client = JsonKeyReaderClient(BASE_URL, USERNAME, PASSWORD)
        await client.login()
        result = await client.run_math(operation, sources)
        print(json.dumps(result, indent=2))
    asyncio.run(run())


if __name__ == "__main__":
    app()
