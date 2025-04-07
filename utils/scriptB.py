
# ===============================
# scriptB.py – JSON Utility Logic
# ===============================
import requests

def get_resource_from_api(url: str) -> dict:
    """
    Fetches a JSON object from the given URL.
    Raises an error if the response is not JSON or is not a top-level dict.
    """
    response = requests.get(url)
    response.raise_for_status()
    json_data = response.json()
    if not isinstance(json_data, dict):
        raise ValueError("Expected top-level JSON object")
    return json_data

def extract_value_from_json(key_path: str, json_data: dict, *, default=None, raise_errors=True) -> any:
    """
    Extracts a value from a potentially deep or irregular JSON object
    using a dot-separated key path like "user.address.city".
    """
    try:
        keys = key_path.split(".")
        value = json_data

        for key in keys:
            if isinstance(value, dict):
                value = value[key]
            elif isinstance(value, list):
                value = value[int(key)]
            else:
                raise KeyError(f"Cannot descend into type {type(value)} at key '{key}'")

        return value

    except Exception as e:
        if raise_errors:
            raise ValueError(f"Failed to extract value from key path '{key_path}': {e}")
        else:
            print(f"[WARN] Failed to extract '{key_path}': {e}")
            return default

def get_value_from_resource(url: str, key: str) -> any:
    """
    Fetches a JSON object from a URL and extracts the value for a given key path.
    Combines `get_resource_from_api` and `get_value_from_data`.
    """
    json_data = get_resource_from_api(url)
    return extract_value_from_json(key_path=key, json_data=json_data)
