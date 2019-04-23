import ast


def estimate_type(string_to_type_estimate):
    """takes a string and return what type it estimates it to be based on ast.literal_eval & internal logic.

            Arguments:
                string_to_type_estimate -- the string a type estimation is needed for
            Returns:
                estimated_type_value -- the value of the string in the estimated type
    """
    if string_to_type_estimate.lower() == "true":
        estimated_type_value = True
    elif string_to_type_estimate.lower() == "false":
        estimated_type_value = False
    else:
        try:
            estimated_type_value = ast.literal_eval(string_to_type_estimate)
        except ValueError:
            estimated_type_value = string_to_type_estimate
    return estimated_type_value
