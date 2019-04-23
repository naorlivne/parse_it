import configparser


def parse_ini_file(path_to_ini_file):
    """take a path to a INI file & returns it as a valid python dict.

            Arguments:
                path_to_ini_file -- the path of the ini file
            Returns:
                config_file_dict -- dict of the file
    """
    config = configparser.ConfigParser()
    config.read(path_to_ini_file)
    my_config_parser_dict = {s: dict(config.items(s)) for s in config.sections()}
    return my_config_parser_dict
