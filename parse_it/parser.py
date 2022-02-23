from parse_it.command_line_args.command_line_args import *
from parse_it.envvars.envvars import *
from parse_it.file.yaml import *
from parse_it.file.ini import *
from parse_it.file.json import *
from parse_it.file.env import *
from parse_it.file.hcl import *
from parse_it.file.toml import *
from parse_it.file.xml import *
from parse_it.type_estimate.type_estimate import *
from parse_it.file.file_reader import *
from typing import Any, Tuple, Optional
import warnings


class ParseIt:

    def __init__(self, config_type_priority: Optional[list] = None, global_default_value: Any = None,
                 type_estimate: bool = True, recurse: bool = False, force_envvars_uppercase: bool = True,
                 config_location: Optional[str] = None, envvar_prefix: Optional[str] = None,
                 custom_suffix_mapping: Optional[dict] = None, envvar_divider: Optional[str] = None,
                 none_values: Optional[set] = None):
        """configures the object which is used to query all types of configuration inputs available and prioritize them
                based on your needs

                    Arguments:
                        config_type_priority -- a list of file types extensions your willing to accept, list order
                            dictates priority of said file types, default list order is as follow:
                            [ "cli_args", "envvars", "env", "json", "yaml", "yml", "toml", "tml", "hcl", "tf", "conf",
                            "cfg", "ini", "xml" ]
                            in the case of multiple files of same type they are all read and the first one that has the
                            needed key is the one used.
                            if no value is returned then the default_value declared at the read_configuration_variable
                            will be used and if that is not configured then the global_default_value will be used
                        global_default_value -- defaults to None, see config_type_priority for it's use
                        type_estimate -- if set to True (True by default) will try to automatically figure out the type
                            of the returned value on it's own, useful for envvars & ini type files which always return a
                            string otherwise
                        recurse -- False by default, if set to True will also look in all subfolders
                        force_envvars_uppercase -- if set to True (which is the default) will force all envvars keys to
                            be UPPERCASE
                        config_location -- the location where the configuration file(s) will be looked for, if None
                            (default) will look in the current working directory, accepts either a directory which will
                            then look in all files in that directory (possibly recursivly depanding on the recurse flag)
                            or if a standard file will look only in said file
                        envvar_prefix -- will add the given prefix for all envvars if set
                        custom_suffix_mapping -- a custom dict which will can map custom file suffixes to a file type
                        envvar_divider -- the divider to split an envvar to nested dicts, if set to None (default) said
                            nesting is disabled
                        none_values -- A tuple with values that should be considered `None`, if set to None (default) it
                            will take the default set tuple of {"", "null", "none"}
        """

        # first we describe the standard file type suffix mapping and what file types are are standard file extensions
        self.suffix_file_type_mapping = {
            "env": [
                "env"
            ],
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
            "env",
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

        if envvar_divider is None:
            self.nest_envvars = False
        else:
            self.nest_envvars = True
            self.envvar_divider = envvar_divider

            # now we add any custom file suffixes the user wanted to the list of possible file extensions and valid
        # suffixes
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
                "env",
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

        if config_location is None:
            self.config_location = os.getcwd()
        else:
            self.config_location = config_location

        # create a list of all valid types
        valid_config_types = []
        for config_type in self.config_type_priority:
            if config_type in self.valid_file_type_extension:
                valid_config_types.append(config_type)

        # we check if the config is a file or a folder
        self.config_file_type = file_or_folder(self.config_location)

        # if config is dict or not declared populate the config_files_dict with the list of locations for each file type
        if self.config_file_type == "folder" or self.config_file_type is None:
            self.config_files_dict = file_types_in_folder(self.config_location, valid_config_types,
                                                          recurse=recurse)
        # if the config is a file populate the config_files_dict with that single file and have the rest file types
        # be blank
        elif self.config_file_type == "file":
            self.config_files_dict = {}
            for file_type_ending in valid_config_types:
                self.config_files_dict[file_type_ending] = []
                if self.config_location.endswith(file_type_ending):
                    self.config_files_dict[file_type_ending].append(self.config_location)

        if none_values is None:
            self.none_values = {"", "null", "none"}
        else:
            self.none_values = none_values

    def read_configuration_variable(self, config_name: str, default_value: Any = None, required: bool = False,
                                    allowed_types: Optional[list] = None) -> Any:
        """reads a single key of the configuration and returns the first value of it found based on the priority of each
                config file option given in the __init__ of the class

                    Arguments:
                        config_name -- the configuration key name you want to get the value of
                        default_value -- defaults to None, see config_type_priority in class init for it's use
                        required -- defaults to False, if set to True will ignore default_value & global_default_value
                            and will raise an ValueError if the configuration is not configured in any of the config
                            files/envvars/cli args
                        allowed_types -- Defaults to None, an optional list of types that are accepted for the variable
                            to be, if set a check will be preformed and if the variables value given is not of any of
                            the types in said list a TypeError will be raised
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
                    # next the envvar if so desired to assist in matching to other file formats
                    if self.nest_envvars is True:
                        config_value = split_envvar(config_name, config_value, divider=self.envvar_divider)
                    break

            # will loop over all files of each type until all files of all types are searched, first time the key is
            # found will break outside of both loops
            elif config_type in self.valid_file_type_extension:
                for config_file in self.config_files_dict[config_type]:
                    if self.config_file_type == "file":
                        file_dict = self._parse_file_per_type(config_type, config_file)
                    else:
                        file_dict = self._parse_file_per_type(config_type, os.path.join(self.config_location,
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
            config_value = estimate_type(config_value, none_values=self.none_values)

        # if the type the config is in the end isn't in the list of allowed_types and allowed_types list is set raise
        # a TypeError
        if allowed_types is not None:
            if type(config_value) not in allowed_types:
                raise TypeError

        return config_value

    def read_multiple_configuration_variables(self, config_names: list, default_value: Any = None,
                                              required: bool = False, allowed_types: Optional[list] = None) -> dict:
        """reads multiple keys of the configuration and returns the first value of each it found based on the priority
                of each config file option given in the __init__ of the class, basically a simple loop of the
                read_configuration_variable function with all the configurable values being the same in all iterations

                    Arguments:
                        config_names -- a list of the configuration key names you want to get the value of
                        default_value -- defaults to None, see config_type_priority in class init for it's use
                        required -- defaults to False, if set to True will ignore default_value & global_default_value
                            and will raise an ValueError if the configuration is not configured in any of the config
                            files/envvars/cli args
                        allowed_types -- Defaults to None, an optional list of types that are accepted for the variable
                            to be, if set a check will be preformed and if the variables value given is not of any of
                            the types in said list a TypeError will be raised
                    Returns:
                        config_value_dict -- a dict of the key/value pairs of all the configurations requested
        """

        config_value_dict = {}
        for config_name in config_names:
            config_value_dict[config_name] = self.read_configuration_variable(config_name, default_value, required,
                                                                              allowed_types)
        return config_value_dict

    def read_all_configuration_variables(self, default_value: Optional[dict] = None, required: Optional[list] = None,
                                         allowed_types: Optional[dict] = None) -> dict:
        """reads all configuration variables from all allowed sources and returns a dict that includes the combined
                        result of all of them, if a configuration variable exists in two (or more) different sources the
                         one with the higher priority will be the only one returned

                    Arguments:
                        default_value -- defaults to None, a dict of key/value pairs of a configuration variables & it's
                            value should it not be defined in any of the valid sources
                        required -- defaults to None, if given a list configuration variables it will raise a ValueError
                            if any of the configuration variables is not configured in any of the config
                            files/envvars/cli args
                        allowed_types -- Defaults to None, an optional dict of types that are accepted for a variable to
                            be, if set a check will be preformed and if the variables value given is not of any of the
                            types in said list a TypeError will be raised
                    Returns:
                        config_value_dict -- a dict of the key/value pairs of all the configurations requested
        """
        # first we create an empty config_value_dict
        config_value_dict = {}

        # now we fill the config_value_dict with the data of all valid sources in reverse order (from least desired to
        # the most desired source), overwriting each data that is found multiple times with the more desired state
        data_sources = self.config_type_priority
        data_sources.reverse()
        for config_type in data_sources:
            if config_type == "cli_args":
                config_value_dict.update(read_all_cli_args_to_dict())
            elif config_type == "envvars" or config_type == "env_vars":
                if self.nest_envvars is True:
                    config_value_dict.update(split_envvar_combained_dict(divider=self.envvar_divider,
                                                                         force_uppercase=self.force_envvars_uppercase))
                else:
                    config_value_dict.update(read_all_envvars_to_dict(force_uppercase=self.force_envvars_uppercase))
            # will loop over all files of each type until all files of all types are searched, first time the key is
            # found will break outside of both loops
            elif config_type in self.valid_file_type_extension:
                for config_file in self.config_files_dict[config_type]:
                    if self.config_file_type == "file":
                        file_dict = self._parse_file_per_type(config_type, config_file)
                    else:
                        file_dict = self._parse_file_per_type(config_type, os.path.join(self.config_location,
                                                                                        config_file))
                    config_value_dict.update(file_dict)
            else:
                raise ValueError

        # now we need to add the default values from the provided "default_value" dict to any configuration variable in
        # said list that wasn't found in any of the valid sources
        if default_value is not None:
            for default_config_key, default_config_value in default_value.items():
                config_found, config_value = self._check_config_in_dict(default_config_key, config_value_dict)
                if config_found is False:
                    config_value_dict[default_config_key] = default_config_value

        # and we run the type estimate (which is recursive) on the full dict if it's configured to be used
        if self.type_estimate is True:
            config_value_dict = estimate_type(config_value_dict, none_values=self.none_values)

        # now we check that all the required values exist and raise a ValueError otherwise
        if required is not None:
            for required_config in required:
                config_found, config_value = self._check_config_in_dict(required_config, config_value_dict)
                if config_found is False:
                    raise ValueError

        # and we also check that the "allowed_types" of all keys in the dict are from the list of allowed types and
        # raise a TypeError
        if allowed_types is not None:
            for allowed_types_key, allowed_types_value in allowed_types.items():
                if type(config_value_dict[allowed_types_key]) not in allowed_types_value:
                    raise TypeError

        # all that's left is returning the combined dict
        return config_value_dict

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
        elif config_file_type in self.suffix_file_type_mapping["env"]:
            file_dict = parse_env_file(config_file_location)
        else:
            raise ValueError
        return file_dict
