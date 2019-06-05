from parse_it.file.file_reader import *
import toml


def parse_toml_file(path_to_toml_file: str) -> dict:
    """take a path to a TOML file & returns it as a valid python dict.

            Arguments:
                path_to_toml_file -- the path of the toml file
            Returns:
                config_file_dict -- dict of the file
    """
    return toml.loads(read_file(path_to_toml_file))
