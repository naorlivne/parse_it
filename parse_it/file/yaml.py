from parse_it.file.file_reader import *
import yaml


def parse_yaml_file(path_to_yaml_file: str) -> dict:
    """take a path to a YAML file & returns it as a valid python dict.

            Arguments:
                path_to_yaml_file -- the path of the yaml file
            Returns:
                config_file_dict -- dict of the file
    """
    return yaml.load(read_file(path_to_yaml_file), Loader=yaml.FullLoader)
