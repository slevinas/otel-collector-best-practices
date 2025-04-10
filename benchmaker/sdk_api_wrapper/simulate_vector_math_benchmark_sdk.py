# simulate_vector_math_benchmark.py

import asyncio
import time
import sys
import json
import random
from benchmaker.sdk_api_wrapper.async_sdk_benchmaker_client import JsonKeyReaderClient


async def simulate_vector_math_benchmark(
        users: int,
        requests_per_user: int,
        delay: float,
        operation: str,
        use_random: bool = False,
        supplied_resource_names: list = None):
    """
    Simulate benchmarking of the run_vectorized_math endpoint.

    Modes:
      1. Auto-generated resource names: For each cycle, resource names are generated uniquely
         using the user id and cycle number. New payloads are stored (using random or deterministic values)
         and then the vector math endpoint is called. Verification is performed for random payloads.

      2. Supplied resource names: If a JSON list is provided via --resource-names,
         those names are used and the script assumes these resources already exist.
         In this mode, store calls are skipped and no verification is performed.

    Args:
        users (int): Number of concurrent simulated users.
        requests_per_user (int): Number of cycles (requests) per user.
        delay (float): Delay between cycles (in seconds).
        operation (str): Math operation ("add" or "subtract").
        use_random (bool): If True, generate random payloads when auto-generating resource names.
        supplied_resource_names (list): If provided, use these resource names (assumed existing) instead of generating names.

    Returns:
        dict: Contains per-user timings and the overall average timing.
    """

    async def simulate_single_user(user_id: int):
        timings = []
        client = JsonKeyReaderClient("http://127.0.0.1:8010", "admin", "admin123")
        await client.login()
        last_result = None  # To store the result from the last cycle

        for cycle in range(1, requests_per_user + 1):
            # If a supplied resource names list is provided, assume these resources already exist.
            if supplied_resource_names is not None:
                resources = supplied_resource_names
                print(f"User {user_id} cycle {cycle}: Using supplied resource names: {resources}")
            else:
                # Generate unique resource names for this user and cycle.
                resourceA = f"A_{user_id}_{cycle}"
                resourceB = f"B_{user_id}_{cycle}"
                resources = [resourceA, resourceB]

            if supplied_resource_names is None:
                # Only perform the store calls if we are auto-generating resources.
                if use_random:
                    # Generate random payloads.
                    val_A_x = random.uniform(0, 10)
                    val_A_y = random.uniform(0, 10)
                    val_B_x = random.uniform(0, 10)
                    val_B_y = random.uniform(0, 10)
                    payload_A = {"x": {"value": val_A_x}, "y": {"value": val_A_y}}
                    payload_B = {"x": {"value": val_B_x}, "y": {"value": val_B_y}}
                else:
                    # Deterministic payloads for testing.
                    payload_A = {"x": {"value": user_id}, "y": {"value": user_id + 2}}
                    payload_B = {"x": {"value": user_id * 2}, "y": {"value": user_id - 1}}

                # Store the generated payloads using unique resource names.
                await client.store(resources[1], payload_B)  # Storing resource B
                await client.store(resources[0], payload_A)  # Storing resource A

            # Time the vector math call.
            start = time.perf_counter()
            last_result = await client.run_math(operation, resources)
            elapsed = time.perf_counter() - start
            timings.append(elapsed)

            # print(f"User {user_id} performed vector math '{operation}' in cycle {cycle} in {elapsed:.4f} seconds")
            # print(f"Result: {last_result}")

            # Verification: Only applicable if using auto-generated random payloads.
            if supplied_resource_names is None and use_random:
                # For "add" operation, verify the sum element-wise.
                expected = {}
                for key in payload_A:
                    try:
                        expected_value = payload_A[key]["value"] + payload_B[key]["value"]
                        expected[key] = {"value": expected_value}
                    except KeyError:
                        expected[key] = None
                if last_result != expected:
                    print(f"❌ Verification Failed for user {user_id} on cycle {cycle}")
                    print(f"   Expected: {expected}, Got: {last_result}")
                else:
                    print(f"✅ Verification Passed for user {user_id} on cycle {cycle}")

            if delay > 0:
                await asyncio.sleep(delay)

        user_avg = sum(timings) / len(timings) if timings else 0
        return {"user_id": user_id, "last_calculation": last_result, "timings": timings, "avg": user_avg}

    # Run all simulated users concurrently.
    results = await asyncio.gather(*(simulate_single_user(uid) for uid in range(1, users + 1)))

    # Aggregate timings.
    all_timings = [t for res in results for t in res["timings"]]
    overall_avg = sum(all_timings) / len(all_timings) if all_timings else 0

    print("\n--- Overall VectorMath Benchmark ---")
    print(f"Total vector_math requests: {len(all_timings)}")
    print(f"Overall average vector_math time: {overall_avg:.4f} seconds")

    return {"results": results, "overall_avg": overall_avg}


if __name__ == "__main__":
    # Expected usage:
    # python simulate_vector_math_benchmark.py <operation> <sources_json> <users> <requests_per_user> [--randomize] [--resource-names '<json_list>']
    #
    # For auto-generated resources, you could run:
    # poetry run python simulate_vector_math_benchmark.py add '[]' 2 5 --randomize
    #
    # For existing resources, supply a JSON list of resource names:
    # poetry run python simulate_vector_math_benchmark.py add '["A","B"]' 2 5 --resource-names '["A","B"]'

    import argparse

    parser = argparse.ArgumentParser(
        description="Simulate vector math benchmark with optional supplied resource names.")
    parser.add_argument("operation", type=str, help="Math operation (e.g., add or subtract)")
    parser.add_argument("sources_json", type=str,
                        help="Dummy JSON for sources (ignored if --resource-names is provided)")
    parser.add_argument("users", type=int, help="Number of concurrent users")
    parser.add_argument("requests_per_user", type=int, help="Number of requests per user")
    parser.add_argument("--randomize", action="store_true", help="Use random payloads (for auto-generated mode only)")
    parser.add_argument("--resource-names", type=str,
                        help="Optional JSON list of resource names to use (existing resources)")

    args = parser.parse_args()

    # Parse the supplied resource names if provided.
    supplied_resource_names = None
    if args.resource_names:
        try:
            supplied_resource_names = json.loads(args.resource_names)
        except json.JSONDecodeError:
            print("Error: --resource-names must be valid JSON.")
            sys.exit(1)

    # Even if sources_json is provided, it will be ignored in auto-generation mode.
    try:
        json.loads(args.sources_json)
    except json.JSONDecodeError:
        print("Error: sources_json must be valid JSON.")
        sys.exit(1)

    asyncio.run(
        simulate_vector_math_benchmark(
            users=args.users,
            requests_per_user=args.requests_per_user,
            delay=0,
            operation=args.operation,
            use_random=args.randomize,
            supplied_resource_names=supplied_resource_names
        )
    )
