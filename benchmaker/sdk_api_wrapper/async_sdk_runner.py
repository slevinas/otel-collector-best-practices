# benchmaker/sdk_api_wrapper/async_load_runner.py

import asyncio
import argparse
from benchmaker.sdk_api_wrapper.async_sdk_benchmaker_client import JsonKeyReaderClient

async def simulate_user(user_id: int):

    print(f"🚀 Starting user {user_id}")
    client = JsonKeyReaderClient("http://127.0.0.1:8010", "admin", "admin123")
    await client.login()

    # Create user-specific payloads for variation
    payload_A = {"x": {"value": user_id}, "y": {"value": user_id + 2}}
    payload_B = {"x": {"value": user_id * 2}, "y": {"value": user_id - 1}}

    await client.store("A", payload_A)
    await client.store("B", payload_B)
    # await client.get_stored("A", key="y")
    # await client.get_stored("A", key="x")
    # await client.get_stored("B",key="x")
    # await client.get_stored("B",key="y")
    result = await client.run_math("add", ["A", "B"])

    print(f"✅ User {user_id} got result: {result}")
    return result

async def main(user_count: int):
    print(f"\n👥 Simulating {user_count} concurrent users...\n")
    await asyncio.gather(*(simulate_user(i) for i in range(1, user_count + 1)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run async SDK load test")
    parser.add_argument("--users", type=int, default=5, help="Number of concurrent users")
    args = parser.parse_args()

    asyncio.run(main(args.users))
