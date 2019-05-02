from parse_it.file.file_reader import *
import xmltodict


def parse_xml_file(path_to_xml_file):
    """take a path to a JSON file & returns it as a valid python dict.

            Arguments:
                path_to_json_file -- the path of the json file
            Returns:
                config_file_dict -- dict of the file
    """
    return xmltodict.parse(read_file(path_to_xml_file))
