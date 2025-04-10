# simulate_login_benchmark_sdk.py

import asyncio
import time
from benchmaker.sdk_api_wrapper.async_sdk_benchmaker_client import JsonKeyReaderClient


async def simulate_login_benchmark(users: int, requests_per_user: int):
    """
    Simulate benchmarking of the /login endpoint.

    Each simulated user performs the login call a given number of times.

    Args:
        users (int): Number of concurrent simulated users.
        requests_per_user (int): Number of login requests each user will perform.

    Returns:
        dict: A dictionary containing per-user timings and the overall average login time.
    """

    async def simulate_single_user(user_id: int):
        # Each simulated user creates its own client and calls login repeatedly.
        timings = []
        client = JsonKeyReaderClient("http://127.0.0.1:8010", "admin", "admin123")

        for i in range(requests_per_user):
            start = time.perf_counter()
            # Perform login call and store the returned token (although token re-use is optional)
            await client.login()
            elapsed = time.perf_counter() - start
            timings.append(elapsed)
            print(f"User {user_id} login {i + 1} completed in {elapsed:.4f} seconds")

        user_avg = sum(timings) / len(timings) if timings else 0
        return {"user_id": user_id, "timings": timings, "avg": user_avg}

    # Run all simulated users concurrently
    results = await asyncio.gather(*(simulate_single_user(user_id) for user_id in range(1, users + 1)))
    # [{'user_id': 1, 'timings': [0.2912240410223603], 'avg': 0.2912240410223603},
    #  {'user_id': 2, 'timings': [0.24808416701853275], 'avg': 0.24808416701853275},
    #  {'user_id': 3, 'timings': [0.24727779207751155], 'avg': 0.24727779207751155}]
    #
    # print("\n--- Results of simulating_single_uer ---")
    # print(results)

    # Aggregate all timings across users
    all_timings = [t for res in results for t in res["timings"]]
    # [0.21309054200537503, 0.1704330421052873, 0.1672944170422852]

    # print("\n--- Results of simulating_single_uer of all_timing of the results ---")
    # print(all_timings)
    overall_avg = sum(all_timings) / len(all_timings) if all_timings else 0

    print("\n--- Overall Login Benchmark ---")
    print(f"Total login requests: {len(all_timings)}")
    print(f"Overall average login time: {overall_avg:.4f} seconds")

    return {"results": results, "overall_avg": overall_avg}



# Test harness to run the login benchmark
if __name__ == "__main__":
    import sys

    # Allow parameters to be passed via command-line, if desired.
    # For simplicity, here we use default values.
    users = 2
    requests_per_user = 5

    # You can also pass these as command-line arguments if you prefer:
    if len(sys.argv) >= 3:
        users = int(sys.argv[1])
        requests_per_user = int(sys.argv[2])

    asyncio.run(simulate_login_benchmark(users, requests_per_user))
