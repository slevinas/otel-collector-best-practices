import typer
import asyncio
from typing import Optional
import json
from simulate_login_benchmark import simulate_login_benchmark

app = typer.Typer()

# Dummy simulation functions to demonstrate. Replace these with your actual benchmark functions.
# In your real implementation, these functions should be imported from your SDK-runner module.

# async def simulate_login_benchmark(users: int, requests_per_user: int):
#     # Simulate running the /login endpoint benchmark. Replace with your actual function.
#     await asyncio.sleep(0.1)  # Simulate async work
#     return f"/login benchmark: {users} users, {requests_per_user} cycles"

async def simulate_store_benchmark(users: int, requests_per_user: int, payload: dict):
    # Simulate running the /store endpoint benchmark.
    await asyncio.sleep(0.1)
    return f"/store benchmark: {users} users, {requests_per_user} cycles, payload={payload}"

async def simulate_run_math_benchmark(users: int, requests_per_user: int, verify: bool = False, use_random: bool = False):
    # Simulate running the /run_vectorized_math benchmark.
    await asyncio.sleep(0.1)
    # For demonstration, we assume the verification check is done inside the simulation function.
    verification = " (verification passed)" if verify and use_random else ""
    return f"/run_vectorized_math benchmark: {users} users, {requests_per_user} cycles{verification}"

@app.command("benchmark")
def benchmark(
    endpoint: Optional[str] = typer.Option(
        None,
        "--endpoint",
        help="API endpoint to benchmark (e.g., \"/login\", \"/store\", \"/run_vectorized_math\")."
    ),
    users: int = typer.Option(
        1, "--users", help="Number of parallel simulated users."
    ),
    requests_per_user: int = typer.Option(
        5, "--requests-per-user", help="Number of requests each user should perform."
    ),
    payload: Optional[str] = typer.Option(
        None,
        "--payload",
        help="Optional JSON payload for the request, e.g. '{\"x\": {\"value\": 1}, \"y\": {\"value\": 2}}'."
    ),
    run_all: bool = typer.Option(
        False, "--run-all", help="Run benchmark on all supported endpoints."
    ),
    verify: bool = typer.Option(
        False, "--verify", help="If using random payloads on /run_vectorized_math, verify the result."
    ),
    use_random: bool = typer.Option(
        False, "--random", help="Use randomized payloads for endpoints that support it."
    )
):
    """
    Run benchmark tests on one or all API endpoints.
    """
    # Convert payload string to dictionary if provided.
    payload_dict = None
    if payload:
        try:
            payload_dict = json.loads(payload)
        except json.JSONDecodeError:
            typer.echo("Payload is not valid JSON. Please supply a valid JSON string.")
            raise typer.Exit(code=1)

    # Determine which endpoints to run.
    endpoints_to_test = []
    if run_all:
        endpoints_to_test = ["/login", "/store", "/run_vectorized_math"]
    else:
        if not endpoint:
            typer.echo("Please supply an endpoint using --endpoint or use --run-all to test all endpoints.")
            raise typer.Exit(code=1)
        endpoints_to_test = [endpoint]

    async def run_benchmarks():
        results = {}
        for ep in endpoints_to_test:
            typer.echo(f"🔍 Running benchmark for endpoint: {ep}")
            if ep == "/login":
                result = await simulate_login_benchmark(users, requests_per_user)
            elif ep == "/store":
                # If no payload is provided, use a default payload.
                effective_payload = payload_dict if payload_dict else {"x": {"value": 1}, "y": {"value": 2}}
                result = await simulate_store_benchmark(users, requests_per_user, effective_payload)
            elif ep == "/run_vectorized_math":
                result = await simulate_run_math_benchmark(users, requests_per_user, verify=verify, use_random=use_random)
            else:
                typer.echo(f"Endpoint {ep} is not recognized for benchmarking.")
                continue
            results[ep] = result
        return results

    # Run the benchmarks asynchronously.
    final_results = asyncio.run(run_benchmarks())

    # Display aggregated results.
    typer.echo("\n📊 Benchmark Results:")
    for ep, res in final_results.items():
        typer.echo(f"{ep}: {res}")

if __name__ == "__main__":
    """
    poetry run python benchmaker_cli.py benchmark --endpoint "/login" --users 2 --requests-per-user 5
"""
    app()
