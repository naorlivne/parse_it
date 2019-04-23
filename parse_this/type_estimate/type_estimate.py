import ast


def estimate_type(string_to_type_estimate):
    """takes a string and return it's value in a type it estimates it to be based on ast.literal_eval & internal logic.

            Arguments:
                string_to_type_estimate -- the string a type estimation is needed for
            Returns:
                estimated_type_value -- the value of the string in the estimated type
    """
    if isinstance(string_to_type_estimate, str):
        lowercase_string = string_to_type_estimate.lower()
        if lowercase_string == "true":
            estimated_type_value = True
        elif lowercase_string == "false":
            estimated_type_value = False
        elif lowercase_string == "" or lowercase_string == "none" or lowercase_string == "null":
            estimated_type_value = None
        else:
            try:
                estimated_type_value = ast.literal_eval(string_to_type_estimate)
            except ValueError:
                estimated_type_value = string_to_type_estimate
    else:
        estimated_type_value = string_to_type_estimate
    return estimated_type_value
