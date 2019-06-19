from parse_it.command_line_args.command_line_args import *
from parse_it.envvars.envvars import *
from parse_it.file.yaml import *
from parse_it.file.ini import *
from parse_it.file.json import *
from parse_it.file.hcl import *
from parse_it.file.toml import *
from parse_it.file.xml import *
from parse_it.type_estimate.type_estimate import *
from parse_it.file.file_reader import *
from typing import Any, Tuple, Optional
import warnings


class ParseIt:

    def __init__(self, config_type_priority: Optional[list] = None, global_default_value: Any = None,
                 type_estimate: bool = True, recurse: bool = True, force_envvars_uppercase: bool = True,
                 config_folder_location: Optional[str] = None, envvar_prefix: Optional[str] = None,
                 custom_suffix_mapping: Optional[dict] = None):
        """configures the object which is used to query all types of configuration inputs available and prioritize them
                based on your needs

                    Arguments:
                        config_type_priority -- a list of file types extensions your willing to accept, list order
                            dictates priority of said file types, default list order is as follow:
                                [ "cli_args", "envvars", "json", "yaml", "yml", "toml", "tml", "hcl", "tf", "conf",
                                "cfg", "ini", "xml" ]
                            in the case of multiple files of same type they are all read and the first one that has the
                                needed key is the one used.
                            if no value is returned then the default_value declared at the read_configuration_variable
                                will be used and if that is not configured then the global_default_value will be used
                        global_default_value -- defaults to None, see config_type_priority for it's use
                        type_estimate -- if set to True (True by default) will try to automatically figure out the type
                            of the returned value on it's own, useful for envvars & ini type files which always return a
                            string otherwise
                        recurse -- True by default, if set to True will also look in all subfolders
                        force_envvars_uppercase -- if set to True (which is the default) will force all envvars keys to
                            be UPPERCASE
                        config_folder_location -- the folder where the configuration files will be looked for, if None
                            (default) will look in the current working directory
                        envvar_prefix -- will add the given prefix for all envvars if set
                        custom_suffix_mapping -- a custom dict which will can map custom file suffixes to a file type
        """

        self.suffix_file_type_mapping = {
            "json": [
                "json"
            ],
            "yaml": [
                "yaml",
                "yml"
            ],
            "toml": [
                "toml",
                "tml"
            ],
            "hcl": [
                "hcl",
                "tf"
            ],
            "ini": [
                "conf",
                "cfg",
                "ini"
            ],
            "xml": [
                "xml"
            ]
        }
        self.valid_file_type_extension = [
            "json",
            "yaml",
            "yml",
            "toml",
            "tml",
            "hcl",
            "tf",
            "conf",
            "cfg",
            "ini",
            "xml"
        ]

        if custom_suffix_mapping is not None:
            for file_type, custom_file_suffix in custom_suffix_mapping.items():
                self.suffix_file_type_mapping[file_type] = self.suffix_file_type_mapping[file_type] + custom_file_suffix
            custom_suffixes_list = [suffix_value for suffix_list in custom_suffix_mapping.values() for suffix_value in
                                    suffix_list]
            self.valid_file_type_extension += custom_suffixes_list
            if config_type_priority is None:
                warnings.warn("custom_suffix_mapping is defined but config_type_priority is using the default setting, "
                              "custom file suffixes will not be used")

        if envvar_prefix is None:
            self.envvar_prefix = ""
        else:
            self.envvar_prefix = envvar_prefix

        self.global_default_value = global_default_value
        self.type_estimate = type_estimate
        self.force_envvars_uppercase = force_envvars_uppercase

        if config_type_priority is None:
            self.config_type_priority = [
                "cli_args",
                "env_vars",
                "json",
                "yaml",
                "yml",
                "toml",
                "tml",
                "hcl",
                "tf",
                "conf",
                "cfg",
                "ini",
                "xml"
            ]

        else:
            self.config_type_priority = config_type_priority
        if config_folder_location is None:
            self.config_folder_location = os.getcwd()
        else:
            self.config_folder_location = config_folder_location
        file_types_in_folder_list = []
        for config_type in self.config_type_priority:
            if config_type in self.valid_file_type_extension:
                file_types_in_folder_list.append(config_type)
        self.config_files_dict = file_types_in_folder(self.config_folder_location, file_types_in_folder_list,
                                                      recurse=recurse)

    def read_configuration_variable(self, config_name: str, default_value: Any = None, required: bool = False) -> Any:
        """reads a single key of the configuration and returns the first value of it found based on the priority of each
                config file option given in the __init__ of the class

                    Arguments:
                        config_name -- the configuration key name you want to get the value of
                        default_value -- defaults to None, see config_type_priority in class init for it's use
                        required -- defaults to False, if set to True will ignore default_value & global_default_value
                            and will raise an ValueError if the configuration is not configured in any of the config
                            files/envvars/cli args
                    Returns:
                        config_value -- the value of the configuration requested
        """

        # we start with both key not found and the value being None
        config_value = None
        config_key_found = False

        # we now loop over all the permitted types of where the config key might be and break on the first one found
        # after setting config_key_found to True and config_value to the value found
        for config_type in self.config_type_priority:
            if config_type == "cli_args":
                config_key_found = command_line_arg_defined(config_name)
                if config_key_found is True:
                    config_value = read_command_line_arg(config_name)
                    break
            elif config_type == "envvars" or config_type == "env_vars":
                config_key_found = envvar_defined(self.envvar_prefix + config_name,
                                                  force_uppercase=self.force_envvars_uppercase)
                config_value = read_envvar(self.envvar_prefix + config_name,
                                           force_uppercase=self.force_envvars_uppercase)
                if config_key_found is True:
                    break
            # will loop over all files of each type until all files of all types are searched, first time the key is
            # found will break outside of both loops
            elif config_type in self.valid_file_type_extension:
                for config_file in self.config_files_dict[config_type]:
                    file_dict = self._parse_file_per_type(config_type, os.path.join(self.config_folder_location,
                                                                                    config_file))
                    config_key_found, config_value = self._check_config_in_dict(config_name, file_dict)
                    if config_key_found is True:
                        break
                if config_key_found is True:
                    break
            else:
                raise ValueError

        # raise error if the key is required and not found in any of the config files, envvar or cli args
        if config_key_found is False and required is True:
            raise ValueError

        # if key is not required but still wasn't found take it from the key default value or failing that from the
        # global default value
        if config_key_found is False:
            if default_value is not None:
                config_value = default_value
            else:
                config_value = self.global_default_value

        # if type estimation is True try to guess the type of the value
        if self.type_estimate is True:
            config_value = estimate_type(config_value)
        return config_value

    @staticmethod
    def _check_config_in_dict(config_key: str, config_dict: dict) -> Tuple[bool, Any]:
        """internal function which checks if the key is in a given dict

            Arguments:
                config_key -- the configuration key name you want to check if it exists in the dict
                config_dict -- the dict you want to check if the is included in
            Returns:
                config_found -- True if the key is in the dict, false otherwise
                config_value -- the value of the configuration requested, returns None if the key is not part of the
                    the dict
        """
        if config_key in config_dict:
            config_value = config_dict[config_key]
            config_found = True
        else:
            config_value = None
            config_found = False
        return config_found, config_value

    def _parse_file_per_type(self, config_file_type: str, config_file_location: str) -> dict:
        """internal function which parses a file to a dict when given the file format type and it's location

            Arguments:
                config_file_type -- the type of the config file
                config_file_location -- the location of the config file
            Returns:
                file_dict -- a parsed dict of the config file data
        """
        if config_file_type in self.suffix_file_type_mapping["json"]:
            file_dict = parse_json_file(config_file_location)
        elif config_file_type in self.suffix_file_type_mapping["yaml"]:
            file_dict = parse_yaml_file(config_file_location)
        elif config_file_type in self.suffix_file_type_mapping["toml"]:
            file_dict = parse_toml_file(config_file_location)
        elif config_file_type in self.suffix_file_type_mapping["ini"]:
            file_dict = parse_ini_file(config_file_location)
        elif config_file_type in self.suffix_file_type_mapping["hcl"]:
            file_dict = parse_hcl_file(config_file_location)
        elif config_file_type in self.suffix_file_type_mapping["xml"]:
            file_dict = parse_xml_file(config_file_location)
        else:
            raise ValueError
        return file_dict
