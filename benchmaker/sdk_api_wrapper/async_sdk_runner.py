import asyncio
from benchmaker.sdk_api_wrapper.async_sdk_benchmaker_client import JsonKeyReaderClient

BASE_URL = "http://127.0.0.1:8010"
USERNAME = "admin"
PASSWORD = "admin123"

async def simulate_user(user_id: int):
    client = JsonKeyReaderClient(BASE_URL, USERNAME, PASSWORD)
    print(f"👤 User {user_id}: Logging in...")
    await client.login()

    name = f"A{user_id}"
    payload = {"x": {"value": user_id}, "y": {"value": user_id * 2}}

    print(f"📦 User {user_id}: Storing {name}...")
    await client.store(name, payload)

    # You can optionally store a second value (like B{user_id}) and run math
    # Then use: await client.run_math("add", [f"A{user_id}", f"B{user_id}"])

async def main():
    users = 100
    await asyncio.gather(*(simulate_user(i) for i in range(users)))

if __name__ == "__main__":
    asyncio.run(main())
