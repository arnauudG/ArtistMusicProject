import sys, os
from contextlib import contextmanager
from typing import Dict, Any

# Define a constant for unknown values
from artist_data.setup import UNKNOWN_VALUE

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout


def safe_get(data: Dict[str, Any], key: str, UNKNOWN_VALUE: Any = UNKNOWN_VALUE) -> Any:
    """
    Safely retrieves the value associated with the given key from a dictionary.

    This function attempts to retrieve the value corresponding to the provided `key` in the dictionary `data`. 
    If the `key` is not found, it returns the specified `UNKNOWN_VALUE`.

    Args:
        data (Dict[str, Any]): The dictionary to retrieve the value from.
        key (str): The key for which the value needs to be retrieved.
        UNKNOWN_VALUE (Any, optional): The value to return if the key is not found. Defaults to 'UNKNOWN'.

    Returns:
        Any: The value associated with the key, or the UNKNOWN_VALUE if the key is not found.
    """
    return data.get(key, UNKNOWN_VALUE)


def extract_value(data: Dict[str, Any], key_path: list, UNKNOWN_VALUE: Any = UNKNOWN_VALUE) -> Any:
    """
    Extracts a value from a nested dictionary based on a list of keys (key path).

    This function traverses a nested dictionary using a list of keys (`key_path`). It goes through each key 
    sequentially to drill down into the dictionary. If any key in the path is missing or leads to an invalid 
    value, it returns the `UNKNOWN_VALUE`.

    Args:
        data (Dict[str, Any]): The dictionary to extract the value from.
        key_path (list): A list of keys representing the path to the target value within the dictionary.
        UNKNOWN_VALUE (Any, optional): The value to return if any key in the path is missing. Defaults to 'UNKNOWN'.

    Returns:
        Any: The value found at the end of the key path, or UNKNOWN_VALUE if not found.
    """
    value = data

    try:
        for key in key_path:
            value = safe_get(value, key, UNKNOWN_VALUE)
            if value == UNKNOWN_VALUE:
                break
    except AttributeError:
        return UNKNOWN_VALUE

    return value if value else UNKNOWN_VALUE


def safe_extract(data: Dict[str, Any], key_path: list, UNKNOWN_VALUE: Any = UNKNOWN_VALUE) -> Any:
    """
    Safely extracts a nested value from a dictionary using a key path.

    This is a wrapper around `extract_value()` that provides a convenient way to retrieve nested values safely 
    from a dictionary. It handles missing keys or intermediate non-dictionary values by returning the 
    `UNKNOWN_VALUE`.

    Args:
        data (Dict[str, Any]): The dictionary to extract the value from.
        key_path (list): A list of keys representing the path to the target value.
        UNKNOWN_VALUE (Any, optional): The value to return if any key in the path is missing. Defaults to 'UNKNOWN'.

    Returns:
        Any: The value found at the specified key path, or UNKNOWN_VALUE if not found.
    """
    return extract_value(data, key_path, UNKNOWN_VALUE)

def flat_nested_dictionary(d: Dict, parent_key: str) -> Dict:
    """Flattens a nested dictionary under a specific key into the parent dictionary."""
    nested_dict = safe_get(d, parent_key, {})
    if isinstance(nested_dict, dict):
        d.update(nested_dict)
    d.pop(parent_key, None)
    return d