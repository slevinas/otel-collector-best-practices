import typer
import asyncio
import json
from typing import Optional

# Import your actual simulation functions.
from simulate_login_benchmark_sdk import simulate_login_benchmark
from simulate_vector_math_benchmark_sdk import simulate_vector_math_benchmark

# Dummy implementation for /store benchmark;
# replace this with your actual simulate_store_benchmark if available.
async def simulate_store_benchmark(users: int, requests_per_user: int, payload: dict):
    await asyncio.sleep(0.1)
    return f"/store benchmark: {users} users, {requests_per_user} cycles, payload={payload}"

app = typer.Typer()

@app.command("benchmark")
def benchmark(
    endpoint: Optional[str] = typer.Option(
        None, "--endpoint", help="API endpoint to benchmark (e.g., \"/login\", \"/store\", \"/run_vectorized_math\")."
    ),
    users: int = typer.Option(
        1, "--users", "-u", help="Number of parallel simulated users."
    ),
    requests_per_user: int = typer.Option(
        5, "--requests-per-user", "-r", help="Number of requests (cycles) each user will perform."
    ),
    delay: float = typer.Option(
        0.0, "--delay", "-d", help="Delay between cycles (in seconds)."
    ),
    payload: Optional[str] = typer.Option(
        None,
        "--payload",
        help="Optional JSON payload for /store endpoint, e.g., '{\"x\": {\"value\": 1}, \"y\": {\"value\": 2}}'."
    ),
    run_all: bool = typer.Option(
        False, "--run-all", help="Run benchmark on all supported endpoints."
    ),
    verify: bool = typer.Option(
        False, "--verify", help="If true and using random payloads for /run_vectorized_math, perform verification."
    ),
    use_random: bool = typer.Option(
        False, "--random", help="Use randomized payloads for endpoints that support it."
    ),
    resource_names: Optional[str] = typer.Option(
        None,
        "--resource-names",
        help="Optional JSON list of resource names to use (e.g. '[\"A\",\"B\"]'). For /run_vectorized_math or /store. When supplied, the benchmark assumes these resources already exist and skips store calls."
    ),
    vm_operation: str = typer.Option(
        "add", "--vm-operation", help="Vector math operation for /run_vectorized_math benchmark (e.g., add, subtract)."
    )
):
    """
    Run benchmark tests on one or all API endpoints.

    Examples:
      • Benchmark /login:
            poetry run python benchmark_cli.py benchmark --endpoint "/login" --users 2 --requests-per-user 5

      • Benchmark /store (with a custom payload):
            poetry run python benchmark_cli.py benchmark --endpoint "/store" --users 2 --requests-per-user 5 --payload '{"x": {"value": 10}, "y": {"value": 20}}'

      • Benchmark /run_vectorized_math using auto-generated resources with random payloads and verification:
            poetry run python benchmark_cli.py benchmark --endpoint "/run_vectorized_math" --users 2 --requests-per-user 5 --random --verify --vm-operation "add"

      • Benchmark /run_vectorized_math on existing resources:
            poetry run python benchmark_cli.py benchmark --endpoint "/run_vectorized_math" --users 2 --requests-per-user 5 --resource-names '["A","B"]'
    """
    # Parse payload if provided.
    payload_dict = None
    if payload:
        try:
            payload_dict = json.loads(payload)
        except json.JSONDecodeError:
            typer.echo("Error: Payload is not valid JSON. Please supply a valid JSON string.")
            raise typer.Exit(code=1)

    # If --run-all is enabled, ignore the --endpoint parameter.
    endpoints_to_test = []
    if run_all:
        endpoints_to_test = ["/login", "/store", "/run_vectorized_math"]
    else:
        if not endpoint:
            typer.echo("Please supply an endpoint using --endpoint or use --run-all to test all endpoints.")
            raise typer.Exit(code=1)
        endpoints_to_test = [endpoint]

    # Parse the supplied resource names if provided.
    supplied_names = None
    if resource_names:
        try:
            supplied_names = json.loads(resource_names)
        except json.JSONDecodeError:
            typer.echo("Error: --resource-names must be valid JSON.")
            raise typer.Exit(code=1)

    async def run_benchmarks():
        results = {}
        for ep in endpoints_to_test:
            typer.echo(f"🔍 Running benchmark for endpoint: {ep}")
            if ep == "/login":
                result = await simulate_login_benchmark(users, requests_per_user)
            elif ep == "/store":
                effective_payload = payload_dict if payload_dict else {"x": {"value": 1}, "y": {"value": 2}}
                result = await simulate_store_benchmark(users, requests_per_user, effective_payload)
            elif ep == "/run_vectorized_math":
                # Call our updated simulation function.
                result = await simulate_vector_math_benchmark(
                    users=users,
                    requests_per_user=requests_per_user,
                    delay=delay,
                    operation=vm_operation,
                    use_random=use_random,
                    supplied_resource_names=supplied_names
                )
            else:
                typer.echo(f"Endpoint {ep} is not recognized for benchmarking.")
                continue
            results[ep] = result
        return results

    final_results = asyncio.run(run_benchmarks())

    typer.echo("\n📊 Benchmark Results:")
    for ep, res in final_results.items():
        typer.echo(f"{ep}: {res}")

if __name__ == "__main__":
    app()
