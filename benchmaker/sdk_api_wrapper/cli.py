## cli.py
import asyncio
import typer
import json
import random  # Import the random module to generate random float values
from benchmaker.sdk_api_wrapper.async_sdk_benchmaker_client import JsonKeyReaderClient

app = typer.Typer()

BASE_URL = "http://127.0.0.1:8010"
USERNAME = "admin"
PASSWORD = "admin123"

@app.command()
def store(
    name: str,
    x: float = typer.Option(None, help="Value for x (ignored if --randomize is set)"),
    y: float = typer.Option(None, help="Value for y (ignored if --randomize is set)"),
    randomize: bool = typer.Option(False, "--randomize", help="Generate random x and y values instead of providing them"),
    min_val: float = typer.Option(0.0, "--min", help="Minimum random value"),
    max_val: float = typer.Option(10.0, "--max", help="Maximum random value")
):
    """
    Store a JSON object under a given name.

    If --randomize is set, x and y values will be randomly generated within the given range.
    Otherwise, x and y values must be provided.
    """
    async def run():
        client = JsonKeyReaderClient(BASE_URL, USERNAME, PASSWORD)
        await client.login()

        if randomize:
            # Generate random x and y values within the provided range.
            x_val = random.uniform(min_val, max_val)
            y_val = random.uniform(min_val, max_val)
        else:
            # Ensure x and y values are provided if not randomizing.
            if x is None or y is None:
                raise typer.BadParameter("x and y values must be provided unless --randomize is set.")
            x_val = x
            y_val = y

        payload = {"x": {"value": x_val}, "y": {"value": y_val}}
        result = await client.store(name, payload)
        print(json.dumps(result, indent=2))

    asyncio.run(run())

if __name__ == "__main__":
    app()



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
