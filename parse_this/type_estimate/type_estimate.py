import ast


def estimate_type(string_to_type_estimate):
    """takes a string and return it's value in a type it estimates it to be based on ast.literal_eval & internal logic.
            if the result is a list or a dict will recurse to run all internal values as well

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
                if isinstance(estimated_type_value, list) is True:
                    recurse_list = []
                    for value in estimated_type_value:
                        recurse_list.append(estimate_type(value))
                    estimated_type_value = recurse_list
                if isinstance(estimated_type_value, dict) is True:
                    recurse_dict = {}
                    for key, value in estimated_type_value.items():
                        recurse_dict[key] = estimate_type(value)
                    estimated_type_value = recurse_dict
            except ValueError:
                estimated_type_value = string_to_type_estimate
    else:
        estimated_type_value = string_to_type_estimate
    return estimated_type_value
