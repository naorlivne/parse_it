from parse_it.file.file_reader import *
import xmltodict
import json


def parse_xml_file(path_to_xml_file):
    """take a path to a XML file & returns it as a valid python dict.

            Arguments:
                path_to_xml_file -- the path of the xml file
            Returns:
                config_file_dict -- dict of the file
    """
    # the dump & load to/from JSON is to change it from ordered dict to a normal dict
    return json.loads(json.dumps(xmltodict.parse(read_file(path_to_xml_file))))
