# async_sdk_runner.py

import asyncio
import argparse
import time
from benchmaker.sdk_api_wrapper.async_sdk_benchmaker_client import JsonKeyReaderClient


async def simulate_user(user_id: int, requests_per_user: int, delay: float):
    """
    Simulate one user making multiple requests.

    Args:
        user_id (int): Unique identifier for this simulated user.
        requests_per_user (int): Number of complete request cycles to perform.
        delay (float): Delay (in seconds) between each cycle.
    Returns:
        dict: Summary of the user's aggregate performance.
    """
    print(f"🚀 Starting user {user_id}")
    client = JsonKeyReaderClient("http://127.0.0.1:8010", "admin", "admin123")
    await client.login()

    total_time = 0.0
    results = []

    for req in range(requests_per_user):
        start = time.perf_counter()
        # Create user-specific payloads for variation
        payload_A = {"x": {"value": user_id}, "y": {"value": user_id + 2}}
        payload_B = {"x": {"value": user_id * 2}, "y": {"value": user_id - 1}}

        # Each user cycle: store two resources and run math
        await client.store("A", payload_A)
        await client.store("B", payload_B)
        result = await client.run_math("add", ["A", "B"])
        elapsed = time.perf_counter() - start
        total_time += elapsed

        results.append({"cycle": req + 1, "result": result, "elapsed": elapsed})
        print(f"🔄 User {user_id} cycle {req + 1}: completed in {elapsed:.4f}s")

        if delay > 0:
            await asyncio.sleep(delay)

    avg_time = total_time / requests_per_user if requests_per_user > 0 else 0.0
    summary = {"user_id": user_id, "total_time": total_time, "avg_time": avg_time, "cycles": results}
    print(f"✅ User {user_id} completed {requests_per_user} cycles in {total_time:.4f}s (avg {avg_time:.4f}s)")
    return summary


async def main(user_count: int, requests_per_user: int, delay: float):
    print(
        f"\n👥 Simulating {user_count} concurrent users, each performing {requests_per_user} cycles with {delay}s delay between cycles...\n")
    # Launch all user simulations concurrently
    all_summaries = await asyncio.gather(
        *(simulate_user(i, requests_per_user, delay) for i in range(1, user_count + 1)))

    # Optionally aggregate and display overall results
    total_time_all = sum(summary["total_time"] for summary in all_summaries)
    total_cycles_all = sum(len(summary["cycles"]) for summary in all_summaries)
    overall_avg = total_time_all / total_cycles_all if total_cycles_all > 0 else 0.0

    print("\n📊 Overall Summary:")
    print(f"- Total users simulated: {user_count}")
    print(f"- Total cycles performed: {total_cycles_all}")
    print(f"- Combined total time: {total_time_all:.4f}s")
    print(f"- Overall average time per cycle: {overall_avg:.4f}s\n")

    return all_summaries


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run async SDK load test with enhanced concurrency and timing metrics")
    parser.add_argument("--users", type=int, default=5, help="Number of concurrent users")
    parser.add_argument("--requests-per-user", type=int, default=3,
                        help="Number of request cycles each user should perform")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay in seconds between each request cycle per user")
    args = parser.parse_args()

    asyncio.run(main(args.users, args.requests_per_user, args.delay))
