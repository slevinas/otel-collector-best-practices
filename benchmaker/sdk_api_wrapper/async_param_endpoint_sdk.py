# async_sdk_runner.py
import asyncio
import argparse
import time
import statistics
from benchmaker.sdk_api_wrapper.async_sdk_benchmaker_client import JsonKeyReaderClient
import uuid  # for generating a unique run id


async def simulate_user(user_id: int, requests_per_user: int, delay: float, verify: bool = False,
                        use_random: bool = False):
    """
    Simulate one user performing multiple API call cycles.

    Each cycle will record timings for:
      - Storing resource A
      - Storing resource B
      - Running vectorized math

    If 'verify' is True and 'use_random' is True, the result of run_math is verified.
    """
    print(f"🚀 Starting user {user_id}")
    client = JsonKeyReaderClient("http://127.0.0.1:8010", "admin", "admin123")
    await client.login()

    # Prepare to track per-endpoint elapsed times
    cycles = []

    for req in range(requests_per_user):
        cycle_timers = {}

        # --- Store Resource A ---
        if use_random:
            # Generate random payload for A:
            import random
            val_A_x = random.uniform(0, 10)
            val_A_y = random.uniform(0, 10)
            payload_A = {"x": {"value": val_A_x}, "y": {"value": val_A_y}}
        else:
            # deterministic payload (for testing)
            payload_A = {"x": {"value": user_id}, "y": {"value": user_id + 2}}

        start = time.perf_counter()
        await client.store("A", payload_A)
        cycle_timers["store_A"] = time.perf_counter() - start

        # --- Store Resource B ---
        if use_random:
            val_B_x = random.uniform(0, 10)
            val_B_y = random.uniform(0, 10)
            payload_B = {"x": {"value": val_B_x}, "y": {"value": val_B_y}}
        else:
            payload_B = {"x": {"value": user_id * 2}, "y": {"value": user_id - 1}}

        start = time.perf_counter()
        await client.store("B", payload_B)
        cycle_timers["store_B"] = time.perf_counter() - start

        # --- Run Vectorized Math (add operation) ---
        start = time.perf_counter()
        result = await client.run_math("add", ["A", "B"])
        cycle_timers["run_math"] = time.perf_counter() - start

        # --- Verification Step for Math Operation ---
        if verify and use_random:
            # Expected: element-wise sum of resource A and B:
            # For each key (assuming keys are the same in A and B)
            expected = {}
            for key in payload_A:
                try:
                    expected_value = payload_A[key]["value"] + payload_B[key]["value"]
                    expected[key] = {"value": expected_value}
                except KeyError:
                    expected[key] = None

            if result != expected:
                print(f"❌ Verification Failed for user {user_id} on cycle {req + 1}")
                print(f"   Expected: {expected}, Got: {result}")
            else:
                print(f"✅ Verification Passed for user {user_id} on cycle {req + 1}")

        cycles.append({
            "cycle": req + 1,
            "timers": cycle_timers,
            "result": result
        })

        print(f"🔄 User {user_id} cycle {req + 1}: {cycle_timers}")

        if delay > 0:
            await asyncio.sleep(delay)

    return {
        "user_id": user_id,
        "cycles": cycles
    }
