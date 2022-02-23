import ast
from typing import Any
from contextlib import suppress


def estimate_type(node: Any, none_values=None) -> Any:
    """ Takes any type and return it's value in a type it estimates it to be based on ast.literal_eval & internal logic,
    if the result is a list or a dict will recurse to run all internal values as well, in case of problems parsing the
    string with ast.literal_eval it will fallback to sticking with the original type
     
            Arguments:
                node -- the string a type estimation is needed for
                none_values -- the values that should be converted to `None`
            Returns:
                node -- the value of the string in the estimated type

    """

    if none_values is None:
        none_values = {"", "null", "none"}

    # this is to support XML type estimation as it returns a dict of all strings
    if isinstance(node, dict):
        node = str(node)

    if isinstance(node, str):
        if node.lower() in {"true", "false"}:
            node = node.title()
        elif node.lower() in none_values:
            node = "None"

        with suppress(ValueError, SyntaxError):
            node = ast.literal_eval(node)
            if isinstance(node, list):
                node = [
                    estimate_type(item, none_values=none_values)
                    for item in node
                ]
            if isinstance(node, dict):
                node = {
                    key: estimate_type(value, none_values=none_values)
                    for key, value in node.items()
                }

    return node
