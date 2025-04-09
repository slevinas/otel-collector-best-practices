
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




def get_value_from_resource(nested_key:str, data:dict):

    """
    Retrieve a nested value from a dictionary using a dot-seperated key string
        Args:
            nested_key(str): Astring with keys seperated by dots, e.g., "z.value".
            data (dict): The JSON dict from which to extract the value.
        Returns:
            The nested value if all keys exist.
        Raises:
            keyError: If a key in the nested path is missing.
            TypeError: If and intermediate value is not a dict.
    """
    if not isinstance(nested_key, str) or not nested_key:
        raise ValueError("The nested key must be a non-empty string.")

    keys = nested_key.split(".")
    value = data

    for k in keys:
        if isinstance(value, dict):
            if k in value:
                value = value[k]
            else:
                raise KeyError(f"Key '{k}' not found at this level. Available keys: {list(value.keys())}")
        else:
            raise TypeError(f"Expected a dictionary at key '{k}', but got a {type(value).__name__} instead.")

    return value



def extract_value_from_json(nested_key: str, data: dict):
    """
    Alias for get_value_from_resource for backward compatibility or convenience.

    Args:
        nested_key (str): A dot-separated key path.
        data (dict): JSON data in dictionary form.

    Returns:
        The nested value.
    """
    return get_value_from_resource(nested_key, data)