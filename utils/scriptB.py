
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



def get_value_from_resource_recursive(nested_key: str, data: dict):
    """
    Retrieve a nested value from a dictionary using a recursive approach.

    Args:
        nested_key (str): A dot-separated key string, e.g., "x.value".
        data (dict): The JSON dictionary from which to extract the value.

    Returns:
        The nested value if all keys exist.

    Raises:
        KeyError: If a key in the nested path is missing.
        TypeError: If an intermediate value is not a dict.
    """
    if not isinstance(nested_key, str) or not nested_key:
        raise ValueError("The nested key must be a non-empty string.")

    # Split only on the first dot
    parts = nested_key.split(".", 1)
    key = parts[0]

    if not isinstance(data, dict):
        raise TypeError(f"Expected a dictionary when looking for key '{key}', but got a {type(data).__name__}")

    if key not in data:
        raise KeyError(f"Key '{key}' not found. Available keys: {list(data.keys())}")

    # If there's only one part, we're at our target value
    if len(parts) == 1:
        return data[key]
    else:
        # Recurse with the remainder of the nested key on the next level of data
        return get_value_from_resource_recursive(parts[1], data[key])


