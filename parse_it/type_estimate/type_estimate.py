import ast
from typing import Any
from contextlib import suppress


def estimate_type(node: str) -> Any:
    """ Takes a string and return it's value in a type it estimates it to be based on ast.literal_eval & internal logic.
    if the result is a list or a dict will recurse to run all internal values as well
     
            Arguments:
                node -- the string a type estimation is needed for
            Returns:
                node -- the value of the string in the estimated type

    """
    if isinstance(node, str):
        if node.lower() in {"true", "false"}:
            node = node.title()
        elif node.lower() in {"", "null", "none"}:
            node = "None"

        with suppress(ValueError):
            node = ast.literal_eval(node)
            if isinstance(node, list):
                node = [estimate_type(item) for item in node]
            if isinstance(node, dict):
                node = {key: estimate_type(value) for key, value in node.items()}
            
    return node
