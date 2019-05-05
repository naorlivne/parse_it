from parse_it.file.file_reader import *
import hcl


def parse_hcl_file(path_to_hcl_file):
    """take a path to a HCL file & returns it as a valid python dict.

            Arguments:
                path_to_hcl_file -- the path of the hcl file
            Returns:
                config_file_dict -- dict of the file
    """
    return hcl.loads(read_file(path_to_hcl_file))
