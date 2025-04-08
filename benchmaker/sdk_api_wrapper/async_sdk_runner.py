import asyncio
from benchmaker.sdk_api_wrapper.async_sdk_benchmaker_client import JsonKeyReaderClient

async def main():
    client = JsonKeyReaderClient("http://127.0.0.1:8010", "admin", "admin123")

    print("\n🔐 Logging in...")
    await client.login()

    print("\n📦 Storing A...")
    await client.store("A", {"x": {"value": 10}, "y": {"value": 4}})

    print("\n📦 Storing B...")
    await client.store("B", {"x": {"value": 2}, "y": {"value": 1}})

    print("\n➕ Running math (add)...")
    result = await client.run_math("add", ["A", "B"])
    print("✅ Math result:", result)

    print("\n📂 Fetching stored A...")
    stored = await client.get_stored("A")
    print("✅ Stored A:", stored)

asyncio.run(main())
