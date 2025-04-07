import typer
from json_key_reader_sdk import (
    JsonKeyReaderClient,
    save_benchmark,
    load_benchmark,
    compare_to_benchmark
)
import time
import random
import json
from pathlib import Path
from datetime import datetime
from typing import List
import requests

app = typer.Typer()

def get_client():
    return JsonKeyReaderClient("http://localhost:8000", "admin", "admin123")

@app.command()
def run(
    endpoint: str = typer.Option(..., "--endpoint", help="The endpoint to test (store, login, lookup, run_math)"),
    name: str = typer.Option("A", "--name", help="Resource name (e.g., A or B)"),
    value: str = typer.Option("", "--value", help="Key path for 'lookup' (e.g. x.value), or JSON string for 'store'"),
    operation: str = typer.Option("add", "--operation", help="Math operation to perform (add or subtract)"),
    sources: List[str] = typer.Option(["A", "B"], "--sources", help="List of resource names for math"),
    benchmark: bool = typer.Option(False, "--benchmark", help="Save result and elapsed time as benchmark")
):
    """
    Run a specific API operation by name (e.g., store, login, run_math, lookup).
    Optionally record result and timing as a benchmark.
    """
    client = get_client()
    start = time.perf_counter()
    result = None

    try:
        if endpoint == "store":
            try:
                data = json.loads(value)
            except json.JSONDecodeError:
                typer.secho("Invalid JSON for value.", fg=typer.colors.RED)
                raise typer.Exit(code=1)
            result = client.store(name, data)

        elif endpoint == "login":
            result = {"token": client.token}

        elif endpoint == "lookup":
            try:
                if value.strip():
                    result = client.get_stored(name, key=value)
                else:
                    result = client.get_stored(name)
            except requests.HTTPError as e:
                typer.secho(f"❌ Lookup failed: {e}", fg=typer.colors.RED)
                raise typer.Exit(code=1)

        elif endpoint == "run_math":
            try:
                result = client.run_math(operation, sources)
            except requests.HTTPError as e:
                detail = e.response.json().get("detail", "Unknown error")
                typer.secho(f"❌ Math operation failed: {detail}", fg=typer.colors.RED)
                raise typer.Exit(code=1)

        else:
            typer.secho(f"❌ Unknown endpoint '{endpoint}'", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        elapsed = time.perf_counter() - start
        typer.echo(json.dumps(result, indent=2))
        typer.echo(f"⏱ Elapsed: {elapsed:.4f}s")

        if benchmark:
            timestamp = datetime.utcnow().isoformat()
            if endpoint == "run_math":
                benchmark_name = f"{endpoint}_{operation}_{''.join(sources)}"
            else:
                benchmark_name = f"{endpoint}_{name}"
            save_benchmark(benchmark_name, {"result": result, "elapsed": elapsed,"timestamp": timestamp})
            typer.secho(f"✅ Benchmark '{benchmark_name}' saved Timestamp:'{timestamp}'", fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"❌ Unexpected error: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
