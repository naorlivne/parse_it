from dotenv import dotenv_values


def parse_env_file(path_to_env_file: str) -> dict:
    """take a path to a env file & returns it as a valid python dict.

            Arguments:
                path_to_env_file -- the path of the json file
            Returns:
                config_file_dict -- dict of the file
    """
    return dotenv_values(dotenv_path=path_to_env_file)
