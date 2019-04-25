from configobj import ConfigObj


def parse_ini_file(path_to_ini_file):
    """take a path to a INI file & returns it as a valid python dict.

            Arguments:
                path_to_ini_file -- the path of the ini file
            Returns:
                config_file_dict -- dict of the file
    """
    config = ConfigObj(path_to_ini_file)
    return dict(config)
