# json_key_reader_sdk.py
import requests

class JsonKeyReaderClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.token = self._login(username, password)

    def _login(self, username: str, password: str) -> str:
        response = requests.post(f"{self.base_url}/login", data={
            "username": username,
            "password": password
        })
        response.raise_for_status()

        token = response.json()["access_token"]
        # print(f"Zigiii login In to API, received token: {token}")
        return token

    def _auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def store(self, name: str, data: dict):
        r = requests.put(f"{self.base_url}/store/{name}", json=data, headers=self._auth_headers())
        r.raise_for_status()
        return r.json()

    def run_math(self, operation: str, sources: list[str]):
        print(f"➡️  Sending math request: {{'operation': {operation}, 'sources': {sources}}}")

        r = requests.post(
            f"{self.base_url}/run_vectorized_math",
            json={"operation": operation, "sources": sources},
            headers=self._auth_headers()
        )
        r.raise_for_status()
        return r.json()

    def get_stored(self, name: str, key: str | None = None):
        url = f"{self.base_url}/store/{name}"
        headers = self._auth_headers()

        if key and key.strip():
            params = {"key": key}
        else:
            params = None

        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()


import json
from pathlib import Path

BENCHMARKS_DIR = Path("benchmarks")
BENCHMARKS_DIR.mkdir(exist_ok=True)



def save_benchmark(name: str, data: dict):
    print(f" Zigi saving benchmark name:{name}:data:{data}")
    path = BENCHMARKS_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved benchmark: {path}")

def load_benchmark(name: str) -> dict:
    path = BENCHMARKS_DIR / f"{name}.json"
    with open(path, "r") as f:
        return json.load(f)

def compare_to_benchmark(current: dict, expected: dict) -> list[str]:
    diffs = []
    for key in expected:
        if key not in current:
            diffs.append(f"❌ Missing key: {key}")
            continue
        current_val = current[key]["value"]
        expected_val = expected[key]["value"]
        if current_val != expected_val:
            diffs.append(f"⚠️  {key}: expected {expected_val}, got {current_val}")
    return diffs


from datetime import datetime
from benchmaker.db.bench_models import Benchmark

async def record_sdk_benchmark(
    db,
    endpoint: str,
    method: str,
    url: str,
    input: dict,
    status: int,
    result: dict,
    name=None,
    key=None,
    operation=None,
    sources=None,
    elapsed=None,
):
    benchmark = Benchmark(
        endpoint=endpoint,
        method=method,
        url=url,
        input=input,
        status=status,
        result=result,
        name=name,
        key=key,
        operation=operation,
        sources=sources,
        elapsed=elapsed,
        timestamp=datetime.utcnow()
    )
    db.add(benchmark)
    await db.commit()
