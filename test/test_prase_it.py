from unittest import TestCase, mock
from parse_it import ParseIt
from parse_it.command_line_args.command_line_args import *
from parse_it.envvars.envvars import *
from parse_it.file.toml import *
from parse_it.file.hcl import *
from parse_it.file.yaml import *
from parse_it.file.json import *
from parse_it.file.ini import *
from parse_it.file.xml import *
from parse_it.file.file_reader import *
from parse_it.type_estimate.type_estimate import *
import os


VALID_FILE_TYPE_EXTENSIONS = [
    "json",
    "yaml",
    "yml",
    "toml",
    "tml",
    "conf",
    "cfg",
    "ini",
    "xml"
]

test_files_location = os.getenv("TEST_FILES_LOCATION", "test_files")


class BaseTests(TestCase):

    def test_command_line_args_empty(self):
        reply = read_command_line_arg("empty_variable")
        self.assertIsNone(reply)

    def test_command_line_arg_defined_false(self):
        reply = command_line_arg_defined("empty_variable")
        self.assertFalse(reply)

    def test_envvars_empty(self):
        reply = read_envvar("empty_variable")
        self.assertIsNone(reply)

    def test_envvars_string(self):
        os.environ["TEST_ENVVAR"] = "TEST_ENVVAR_VALUE"
        reply = read_envvar("TEST_ENVVAR")
        self.assertEqual(reply, "TEST_ENVVAR_VALUE")

    def test_envvars_string_forced_uppercase(self):
        os.environ["TEST_ENVVAR_UPPERCASE"] = "TEST_ENVVAR_UPPERCASE_VALUE"
        reply = read_envvar("test_envvar_uppercase", force_uppercase=True)
        self.assertEqual(reply, "TEST_ENVVAR_UPPERCASE_VALUE")

    def test_envvars_string_forced_lowercase(self):
        os.environ["test_envvvar_lowercase"] = "test_envvvar_lowercase_value"
        reply = read_envvar("test_envvvar_lowercase", force_uppercase=False)
        self.assertEqual(reply, "test_envvvar_lowercase_value")

    def test_file_reader_read_file(self):
        reply = read_file(test_files_location + "/test_read_file")
        self.assertEqual(reply, "it_reads!")

    def test_file_reader_read_file_does_not_exist(self):
        reply = read_file(test_files_location + "/totally_bogus_file")
        self.assertIsNone(reply)

    def test_file_reader_folder_exists(self):
        reply = folder_exists(test_files_location)
        self.assertTrue(reply)

    def test_file_reader_folder_does_not_exists(self):
        reply = folder_exists("totally_bogus_directory")
        self.assertFalse(reply)

    def test_file_reader_strip_trailing_slash(self):
        reply = strip_trailing_slash(test_files_location + "/")
        self.assertEqual(reply, test_files_location)

    def test_file_reader_strip_trailing_slash_root_folder(self):
        reply = strip_trailing_slash("/")
        self.assertEqual(reply, "/")

    def test_file_reader_strip_trailing_slash_no_strip_needed(self):
        reply = strip_trailing_slash(test_files_location)
        self.assertEqual(reply, test_files_location)

    def test_file_reader_file_types_in_folder_folder_does_not_exist_raise_warn(self):
        with self.assertWarns(Warning):
            file_types_in_folder("totally_bogus_folder_location", VALID_FILE_TYPE_EXTENSIONS)

    def test_read_envvar_folder_does_not_exist_raise_warn(self):
        with self.assertWarns(Warning):
            os.environ["TEST_CONFIG_FOLDER_NON_EXISTING_ENVVAR"] = "TEST_CONFIG_FOLDER_NON_EXISTING_ENVVAR"
            parser = ParseIt(config_folder_location="totally_bogus_folder_location", config_type_priority=[
                "yaml",
                "json",
                "env_vars"
            ])
            reply = parser.read_configuration_variable("test_config_folder_non_existing_envvar")
            self.assertEqual(reply, "TEST_CONFIG_FOLDER_NON_EXISTING_ENVVAR")

    def test_read_cli_args_folder_does_not_exist_raise_warn(self):
        with self.assertWarns(Warning):
            ParseIt(config_folder_location="totally_bogus_folder_location", config_type_priority=[
                "yaml",
                "json",
                "cli_args"
            ])
            testargs = ["parse_it_mock_script.py", "--test_cli_key_no_folder", "test_value"]
            with mock.patch('sys.argv', testargs):
                parser = ParseIt()
                reply = parser.read_configuration_variable("test_cli_key_no_folder")
                self.assertEqual(reply, "test_value")

    def test_file_reader_file_types_in_folder(self):
        reply = file_types_in_folder(test_files_location, VALID_FILE_TYPE_EXTENSIONS)
        expected_reply = {
            'json': [
                'test.json',
                'test_subfolder_1/test_sub_subfolder_2/test_subfolder_2.json',
                'test_subfolder_1/test_sub_subfolder_3/test_subfolder_3.json',
                'test_subfolder_1/test_subfolder_1.json'
            ],
            'yaml': [
                'test.yaml'
            ],
            'yml': [],
            'toml': [
                'test.toml'
            ],
            'tml': [],
            'conf': [],
            'cfg': [],
            'ini': [
                'test.ini'
            ],
            'xml': [
                'test.xml'
            ]
        }
        self.assertEqual(reply, expected_reply)

    def test_ini(self):
        reply = parse_ini_file(test_files_location + "/test.ini")
        expected_reply = {
            'DEFAULT': {
                'file_type': "ini",
                'test_string': 'testing',
                'test_bool_true': 'true',
                'test_bool_false': 'false',
                'test_int': '123.0',
                'test_float': '123.123',
                'test_list': '["test1", "test2", "test3"]'
            },
            'test_ini': {
                'test_ini_key': 'test_ini_value'
            }
        }
        self.assertEqual(reply, expected_reply)

    def test_json(self):
        reply = parse_json_file(test_files_location + "/test.json")
        expected_reply = {
            'file_type': "json",
            'test_string': 'testing',
            'test_bool_true': True,
            'test_bool_false': False,
            'test_int': 123,
            'test_float': 123.123,
            'test_list': [
                'test1',
                'test2',
                'test3'
            ],
            'test_json': {
                'test_json_key': 'test_json_value'
            }
        }
        self.assertEqual(reply, expected_reply)

    def test_hcl(self):
        reply = parse_hcl_file(test_files_location + "/test.hcl")
        expected_reply = {
            'file_type': "hcl",
            'test_string': 'testing',
            'test_bool_true': True,
            'test_bool_false': False,
            'test_int': 123,
            'test_float': 123.123,
            'test_list': [
                'test1',
                'test2',
                'test3'
            ],
            'test_hcl': {
                'test_hcl_name': {
                    'test_hcl_key': 'test_hcl_value'
                }
            }
        }
        self.assertEqual(reply, expected_reply)

    def test_xml(self):
        reply = parse_xml_file(test_files_location + "/test.xml")
        expected_reply = {
            "xml_root": {
                'file_type': 'xml',
                'test_bool_false': 'false',
                'test_bool_true': 'true',
                'test_float': '123.123',
                'test_int': '123',
                'test_xml': {
                    'test_xml_key': 'test_xml_value'
                },
                'test_list': {
                    'element': [
                        'test1',
                        'test2',
                        'test3'
                    ]
                },
                'test_string': 'testing'
            }
        }
        self.assertEqual(reply, expected_reply)

    def test_toml(self):
        reply = parse_toml_file(test_files_location + "/test.toml")
        expected_reply = {
            'file_type': "toml",
            'test_string': 'testing',
            'test_bool_true': True,
            'test_bool_false': False,
            'test_int': 123,
            'test_float': 123.123,
            'test_list': [
                'test1',
                'test2',
                'test3'
            ],
            'test_toml': {
                'test_toml_key': 'test_toml_value'
            }
        }
        self.assertEqual(reply, expected_reply)

    def test_yaml(self):
        reply = parse_yaml_file(test_files_location + "/test.yaml")
        expected_reply = {
            'file_type': "yaml",
            'test_string': 'testing',
            'test_bool_true': True,
            'test_bool_false': False,
            'test_int': 123,
            'test_float': 123.123,
            'test_list': [
                'test1',
                'test2',
                'test3'
            ],
            'test_yaml': {
                'test_yaml_key': 'test_yaml_value'
            }
        }
        self.assertEqual(reply, expected_reply)

    def test_type_estimate_string(self):
        reply = estimate_type("this_is_a_string")
        self.assertEqual(reply, "this_is_a_string")

    def test_type_estimate_string_complex(self):
        reply = estimate_type("kafka:8082")
        self.assertEqual(reply, "kafka:8082")

    def test_type_estimate_string_very_complex(self):
        reply = estimate_type("https://test//seg34\\^#%#^&@@GGH\nE#TGddvs.36230.54164:8082")
        self.assertEqual(reply, "https://test//seg34\\^#%#^&@@GGH\nE#TGddvs.36230.54164:8082")

    def test_type_estimate_false(self):
        reply_lowercase = estimate_type("false")
        reply_uppercase = estimate_type("FALSE")
        reply_mixed = estimate_type("False")
        self.assertEqual(reply_lowercase, False)
        self.assertEqual(reply_uppercase, False)
        self.assertEqual(reply_mixed, False)

    def test_type_estimate_true(self):
        reply_lowercase = estimate_type("true")
        reply_uppercase = estimate_type("TRUE")
        reply_mixed = estimate_type("True")
        self.assertEqual(reply_lowercase, True)
        self.assertEqual(reply_uppercase, True)
        self.assertEqual(reply_mixed, True)

    def test_type_estimate_int(self):
        reply = estimate_type("123")
        self.assertEqual(reply, 123)

    def test_type_estimate_float(self):
        reply = estimate_type("123.123")
        self.assertEqual(reply, 123.123)

    def test_type_estimate_list(self):
        reply = estimate_type("['test1', 123, True]")
        self.assertEqual(reply, ['test1', 123, True])
        reply = estimate_type('["test1", "test2", "test3"]')
        self.assertEqual(reply, ["test1", "test2", "test3"])
        reply = estimate_type('["test1", {"test_key": "test_value"}, "test3", None]')
        self.assertEqual(reply, ["test1", {"test_key": "test_value"}, "test3", None])

    def test_type_estimate_dict(self):
        reply = estimate_type("{'test_key': ['test1', 123, {'key': 'value'}]}")
        self.assertEqual(reply, {'test_key': ['test1', 123, {'key': 'value'}]})

    def test_type_estimate_none(self):
        reply_empty = estimate_type("")
        reply_lowercase = estimate_type("none")
        reply_null = estimate_type("null")
        reply_uppercase = estimate_type("NONE")
        reply_mixed = estimate_type("None")
        self.assertEqual(reply_empty, None)
        self.assertEqual(reply_lowercase, None)
        self.assertEqual(reply_null, None)
        self.assertEqual(reply_uppercase, None)
        self.assertEqual(reply_mixed, None)

    def test_parser_init(self):
        expected_config_files_dict = {
            'json': [
                'test.json',
                'test_subfolder_1/test_sub_subfolder_2/test_subfolder_2.json',
                'test_subfolder_1/test_sub_subfolder_3/test_subfolder_3.json',
                'test_subfolder_1/test_subfolder_1.json'
            ],
            'yaml': [
                'test.yaml'
            ],
            'yml': [],
            'toml': ['test.toml'],
            'tml': [],
            'hcl': ['test.hcl'],
            'tf': [],
            'conf': [],
            'cfg': [],
            'ini': [
                'test.ini'
            ],
            'xml': [
                'test.xml'
            ]
        }
        expected_config_type_priority = ['cli_args', 'env_vars', 'json', 'yaml', 'yml', 'toml', 'tml', 'hcl', 'tf',
                                         'conf', 'cfg', 'ini', 'xml']
        parser = ParseIt(config_type_priority=None, global_default_value=None, type_estimate=True,
                         force_envvars_uppercase=True, config_folder_location=test_files_location, envvar_prefix=None)
        self.assertEqual(parser.config_files_dict, expected_config_files_dict)
        self.assertEqual(parser.config_folder_location, test_files_location)
        self.assertEqual(parser.config_type_priority, expected_config_type_priority)
        self.assertEqual(parser.envvar_prefix, '')
        self.assertTrue(parser.force_envvars_uppercase)
        self.assertIsNone(parser.global_default_value)
        self.assertTrue(parser.type_estimate)

    def test_parser_custom_suffix_mapping_set_config_type_priority_not_set_raise_warning(self):
        with self.assertWarns(Warning):
            ParseIt(config_folder_location=test_files_location, custom_suffix_mapping={"yaml": ["custom"]})

    def test_parser_custom_suffix_mapping_set(self):
        parser = ParseIt(config_folder_location=test_files_location, custom_suffix_mapping={"yaml": ["custom"]},
                         config_type_priority=["custom"] + VALID_FILE_TYPE_EXTENSIONS)
        expected_config_type_priority = ["custom"] + VALID_FILE_TYPE_EXTENSIONS
        expected_valid_type_extension = ['json', 'yaml', 'yml', 'toml', 'tml', 'hcl', 'tf', 'conf', 'cfg', 'ini', 'xml',
                                         'custom']
        expected_suffix_file_type_mapping = {
            'json': [
                'json'
            ],
            'yaml': [
                'yaml',
                'yml',
                'custom'
            ],
            'toml': [
                'toml',
                'tml'
            ],
            'hcl': [
                'hcl',
                'tf'
            ],
            'ini': [
                'conf',
                'cfg',
                'ini'
            ],
            'xml': [
                'xml'
            ]
        }
        reply = parser.read_configuration_variable("test_string")
        self.assertEqual("testing_custom", reply)
        reply = parser.read_configuration_variable("test_json")
        self.assertEqual({'test_json_key': 'test_json_value'}, reply)
        self.assertEqual(expected_config_type_priority, parser.config_type_priority)
        self.assertEqual(expected_valid_type_extension, parser.valid_file_type_extension)
        self.assertEqual(expected_suffix_file_type_mapping, parser.suffix_file_type_mapping)

    def test_parser_read_configuration_variable(self):
        parser = ParseIt(config_folder_location=test_files_location)
        reply_json = parser.read_configuration_variable("file_type")
        self.assertEqual(reply_json, "json")
        reply_yaml = parser.read_configuration_variable("test_yaml")
        self.assertEqual(reply_yaml, {'test_yaml_key': 'test_yaml_value'})

    def test_parser_read_configuration_subfolder(self):
        parser = ParseIt(config_folder_location=test_files_location)
        reply = parser.read_configuration_variable("test_json_subfolder")
        self.assertTrue(reply)

    def test_parser_read_configuration_recurse_false(self):
        parser = ParseIt(config_folder_location=test_files_location, recurse=False)
        reply = parser.read_configuration_variable("test_json_subfolder")
        expected_config_files_dict = {
            'json': [
                'test.json'
            ],
            'yaml': [
                'test.yaml'
            ],
            'yml': [],
            'toml': [
                'test.toml'
            ],
            'tml': [],
            'conf': [],
            'hcl': ['test.hcl'],
            'tf': [],
            'cfg': [],
            'ini': [
                'test.ini'
            ],
            'xml': [
                'test.xml'
            ]
        }
        self.assertEqual(parser.config_files_dict, expected_config_files_dict)
        self.assertIsNone(reply)

    def test_parser_read_configuration_variable_default_value(self):
        parser = ParseIt(config_folder_location=test_files_location)
        reply = parser.read_configuration_variable("file_type123", default_value="test123")
        self.assertEqual(reply, "test123")

    def test_parser_read_configuration_variable_required_true_value_not_given(self):
        parser = ParseIt(config_folder_location=test_files_location)
        with self.assertRaises(ValueError):
            parser.read_configuration_variable("file_type123", required=True)

    def test_parser_config_type_priority_wrong_type_given(self):
        with self.assertRaises(ValueError):
            parser = ParseIt(config_type_priority=['non_existing_type', 'json'])
            parser.read_configuration_variable("file_type123", required=True)

    def test_parser_read_configuration_variable_required_true_value_given_file(self):
        parser = ParseIt(config_folder_location=test_files_location)
        reply_json = parser.read_configuration_variable("file_type", required=True)
        self.assertEqual(reply_json, "json")

    def test_parser_read_configuration_variable_required_true_value_given_envvar(self):
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_INT"] = "123"
        parser = ParseIt(config_folder_location=test_files_location)
        reply_json = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_INT", required=True)
        self.assertEqual(reply_json, 123)

    def test_parser_read_configuration_variable_global_default_value(self):
        parser = ParseIt(global_default_value="my_last_resort", config_folder_location=test_files_location)
        reply = parser.read_configuration_variable("this_does_not_exist")
        self.assertEqual(reply, "my_last_resort")

    def test_parser_read_configuration_variable_config_type_priority(self):
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_INT"] = "123"
        parser = ParseIt(config_type_priority=["yaml", "toml", "ini", "json", "envvars"],
                         config_folder_location=test_files_location)
        reply = parser.read_configuration_variable("file_type")
        self.assertEqual(reply, "yaml")
        reply = parser.read_configuration_variable("test_toml")
        self.assertEqual(reply, {'test_toml_key': 'test_toml_value'})
        reply = parser.read_configuration_variable("test_ini")
        self.assertEqual(reply, {'test_ini_key': 'test_ini_value'})
        reply = parser.read_configuration_variable("test_json")
        self.assertEqual(reply, {'test_json_key': 'test_json_value'})
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_INT")
        self.assertEqual(reply, 123)

    def test_parser_read_configuration_variable_type_estimate_false(self):
        parser = ParseIt(type_estimate=False, config_folder_location=test_files_location)
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_INT"] = "123"
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_STRING"] = "test"
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_BOOL_TRUE"] = "true"
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_BOOL_FALSE"] = "false"
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_LIST"] = "['test', False, 3]"
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_DICT"] = "{'string': 'string', 'int': 1}"
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_RECURSIVE_LIST"] = "['test', False, 3, ['test', True, 35, {'test': 12}]]"
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_RECURSIVE_DICT"] = "{'string': 'string', 'int': 1, 'dict': " \
                                                                  "{'test': [1, 2]}}"
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_FALSE_INT")
        self.assertEqual(reply, "123")
        self.assertNotEqual(reply, 123)
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_FALSE_STRING")
        self.assertEqual(reply, "test")
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_FALSE_BOOL_TRUE")
        self.assertEqual(reply, "true")
        self.assertNotEqual(reply, True)
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_FALSE_BOOL_FALSE")
        self.assertEqual(reply, "false")
        self.assertNotEqual(reply, False)
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_FALSE_LIST")
        self.assertEqual(reply, "['test', False, 3]")
        self.assertNotEqual(reply, ['test', False, 3])
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_FALSE_DICT")
        self.assertEqual(reply, "{'string': 'string', 'int': 1}")
        self.assertNotEqual(reply, {'string': 'string', 'int': 1})
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_FALSE_RECURSIVE_LIST")
        self.assertEqual(reply, "['test', False, 3, ['test', True, 35, {'test': 12}]]")
        self.assertNotEqual(reply, ['test', False, 3, ['test', True, 35, {'test': 12}]])
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_FALSE_RECURSIVE_DICT")
        self.assertEqual(reply, "{'string': 'string', 'int': 1, 'dict': {'test': [1, 2]}}")
        self.assertNotEqual(reply, {'string': 'string', 'int': 1, 'dict': {'test': [1, 2]}})

    def test_parser_read_configuration_variable_type_estimate_true(self):
        parser = ParseIt(type_estimate=True, config_folder_location=test_files_location)
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_INT"] = "123"
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_STRING"] = "test"
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_BOOL_TRUE"] = "true"
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_BOOL_FALSE"] = "false"
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_LIST"] = "['test', False, 3]"
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_DICT"] = "{'string': 'string', 'int': 1}"
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_RECURSIVE_LIST"] = "['test', False, 3, ['test', True, 35, {'test': 12}]]"
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_RECURSIVE_DICT"] = "{'string': 'string', 'int': 1, 'dict': " \
                                                                 "{'test': [1, 2]}}"
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_INT")
        self.assertNotEqual(reply, "123")
        self.assertEqual(reply, 123)
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_STRING")
        self.assertEqual(reply, "test")
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_BOOL_TRUE")
        self.assertNotEqual(reply, "true")
        self.assertEqual(reply, True)
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_BOOL_FALSE")
        self.assertNotEqual(reply, "false")
        self.assertEqual(reply, False)
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_LIST")
        self.assertNotEqual(reply, "['test', False, 3]")
        self.assertEqual(reply, ['test', False, 3])
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_DICT")
        self.assertNotEqual(reply, "{'string': 'string', 'int': 1}")
        self.assertEqual(reply, {'string': 'string', 'int': 1})
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_RECURSIVE_LIST")
        self.assertNotEqual(reply, "['test', False, 3, ['test', True, 35, {'test': 12}]]")
        self.assertEqual(reply, ['test', False, 3, ['test', True, 35, {'test': 12}]])
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_RECURSIVE_DICT")
        self.assertNotEqual(reply, "{'string': 'string', 'int': 1, 'dict': {'test': [1, 2]}}")
        self.assertEqual(reply, {'string': 'string', 'int': 1, 'dict': {'test': [1, 2]}})

    def test_parser_read_configuration_variable_force_envvars_uppercase_true(self):
        parser = ParseIt(force_envvars_uppercase=True)
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_INT"] = "123"
        os.environ["test_envvar_estimate_true_int"] = "456"
        reply = parser.read_configuration_variable("test_envvar_estimate_true_int")
        self.assertEqual(reply, 123)
        self.assertNotEqual(reply, 456)

    def test_parser_read_configuration_variable_force_envvars_uppercase_false(self):
        parser = ParseIt(force_envvars_uppercase=False, config_folder_location=test_files_location)
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_INT"] = "123"
        os.environ["test_envvar_estimate_true_int"] = "456"
        reply = parser.read_configuration_variable("test_envvar_estimate_true_int")
        self.assertNotEqual(reply, 123)
        self.assertEqual(reply, 456)

    def test_parser_read_configuration_variable_config_folder_location(self):
        parser = ParseIt(config_folder_location=test_files_location)
        reply_json = parser.read_configuration_variable("file_type")
        self.assertEqual(reply_json, "json")
        reply_json = parser.read_configuration_variable("test_float")
        self.assertEqual(reply_json, 123.123)
        reply_yaml = parser.read_configuration_variable("test_yaml")
        self.assertEqual(reply_yaml, {'test_yaml_key': 'test_yaml_value'})
        reply_xml = parser.read_configuration_variable("xml_root")
        expected_reply_xml = {
            'file_type': 'xml',
            'test_bool_false': False,
            'test_bool_true': True,
            'test_float': 123.123,
            'test_int': 123,
            'test_xml': {
                'test_xml_key': 'test_xml_value'
            },
            'test_list': {
                'element': [
                    'test1',
                    'test2',
                    'test3'
                ]
            },
            'test_string': 'testing'
        }
        self.assertEqual(reply_xml, expected_reply_xml)
        reply_hcl = parser.read_configuration_variable("test_hcl")
        expected_reply_hcl = {
            'test_hcl_name': {
                'test_hcl_key': 'test_hcl_value'
            }
        }
        self.assertEqual(reply_hcl, expected_reply_hcl)

    def test_parser_read_configuration_variable_envvar_prefix(self):
        parser = ParseIt(envvar_prefix="prefix_test_", config_folder_location=test_files_location)
        os.environ["PREFIX_TEST_TEST_ENVVAR_ESTIMATE_TRUE_INT"] = "123"
        reply = parser.read_configuration_variable("test_envvar_estimate_true_int")
        self.assertEqual(reply, 123)

    def test_envvar_defined_true(self):
        os.environ["TEST_ENV"] = "123"
        reply = envvar_defined("TEST_ENV")
        self.assertTrue(reply)

    def test_envvar_defined_false(self):
        reply = envvar_defined("TEST_ENV")
        self.assertFalse(reply)

    def test_envvar_defined_true_upper_case(self):
        os.environ["TEST_ENV"] = "123"
        reply = envvar_defined("test_env", force_uppercase=True)
        self.assertTrue(reply)

    def test_envvar_defined_false_upper_case(self):
        os.environ["TEST_ENV"] = "123"
        reply = envvar_defined("test_env", force_uppercase=False)
        self.assertFalse(reply)

    def test_parser_config_found_in_key(self):
        parser = ParseIt(config_folder_location=test_files_location)
        config_found_reply, config_value_reply = parser._check_config_in_dict("test_key", {"test_key": "test_value"})
        self.assertTrue(config_found_reply)
        self.assertEqual(config_value_reply, "test_value")

    def test_parser_config_found_in_key_false(self):
        parser = ParseIt(config_folder_location=test_files_location)
        config_found_reply, config_value_reply = parser._check_config_in_dict("wrong_key", {"test_key": "test_value"})
        self.assertFalse(config_found_reply)
        self.assertEqual(config_value_reply, None)

    def test_parser__parse_file_per_type_wrong_type(self):
        parser = ParseIt(config_folder_location=test_files_location)
        with self.assertRaises(ValueError):
            parser._parse_file_per_type("non_existing_type", test_files_location + "/test.json")

    def test_parser__parse_file_per_type_json(self):
        parser = ParseIt(config_folder_location=test_files_location)
        reply = parser._parse_file_per_type("json", test_files_location + "/test.json")
        expected_reply = {
            'file_type': 'json',
            'test_string': 'testing',
            'test_bool_true': True,
            'test_bool_false': False,
            'test_int': 123,
            'test_float': 123.123,
            'test_list': [
                'test1',
                'test2',
                'test3'
            ],
            'test_json': {
                'test_json_key': 'test_json_value'
            }
        }
        self.assertEqual(reply, expected_reply)

    def test_parser__parse_file_per_type_yaml(self):
        parser = ParseIt(config_folder_location=test_files_location)
        reply = parser._parse_file_per_type("yaml", test_files_location + "/test.yaml")
        expected_reply = {
            'file_type': 'yaml',
            'test_string': 'testing',
            'test_bool_true': True,
            'test_bool_false': False,
            'test_int': 123,
            'test_float': 123.123,
            'test_list': [
                'test1',
                'test2',
                'test3'
            ],
            'test_yaml': {
                'test_yaml_key': 'test_yaml_value'
            }
        }
        self.assertEqual(reply, expected_reply)
        reply = parser._parse_file_per_type("yml", test_files_location + "/test.yaml")
        self.assertEqual(reply, expected_reply)

    def test_parser__parse_file_per_type_custom_yaml(self):
        parser = ParseIt(config_folder_location=test_files_location, custom_suffix_mapping={"yaml": ["custom"]},
                         config_type_priority=["custom"] + VALID_FILE_TYPE_EXTENSIONS)
        reply = parser._parse_file_per_type("custom", test_files_location + "/test.custom")
        expected_reply = {
            'file_type': 'custom_yaml_suffix',
            'test_string': 'testing_custom',
            'test_bool_true': True,
            'test_bool_false': False,
            'test_int': 123,
            'test_float': 123.123,
            'test_list': [
                'test1',
                'test2',
                'test3'
            ],
            'test_yaml': {
                'test_yaml_key': 'custom_test_yaml_value'
            }
        }
        self.assertEqual(reply, expected_reply)

    def test_parser__parse_file_per_type_toml(self):
        parser = ParseIt(config_folder_location=test_files_location)
        reply = parser._parse_file_per_type("toml", test_files_location + "/test.toml")
        expected_reply = {
            'file_type': 'toml',
            'test_string': 'testing',
            'test_bool_true': True,
            'test_bool_false': False,
            'test_int': 123,
            'test_float': 123.123,
            'test_list': [
                'test1',
                'test2',
                'test3'
            ],
            'test_toml': {
                'test_toml_key': 'test_toml_value'
            }
        }
        self.assertEqual(reply, expected_reply)
        reply = parser._parse_file_per_type("tml", test_files_location + "/test.toml")
        self.assertEqual(reply, expected_reply)

    def test_parser__parse_file_per_type_hcl(self):
        parser = ParseIt(config_folder_location=test_files_location)
        reply = parser._parse_file_per_type("hcl", test_files_location + "/test.hcl")
        expected_reply = {
            'file_type': 'hcl',
            'test_string': 'testing',
            'test_bool_true': True,
            'test_bool_false': False,
            'test_int': 123,
            'test_float': 123.123,
            'test_list': [
                'test1',
                'test2',
                'test3'
            ],
            'test_hcl': {
                "test_hcl_name": {
                    'test_hcl_key': 'test_hcl_value'
                }
            }
        }
        self.assertEqual(reply, expected_reply)
        reply = parser._parse_file_per_type("tf", test_files_location + "/test.hcl")
        self.assertEqual(reply, expected_reply)

    def test_parser__parse_file_per_type_ini(self):
        parser = ParseIt(config_folder_location=test_files_location)
        reply = parser._parse_file_per_type("ini", test_files_location + "/test.ini")
        expected_reply = {
            'DEFAULT': {
                'file_type': 'ini',
                'test_string': 'testing',
                'test_bool_true': 'true',
                'test_bool_false': 'false',
                'test_int': '123.0',
                'test_float': '123.123',
                'test_list': '["test1", "test2", "test3"]'
            },
            'test_ini': {
                'test_ini_key': 'test_ini_value'
            }
        }
        self.assertEqual(reply, expected_reply)
        reply = parser._parse_file_per_type("conf", test_files_location + "/test.ini")
        self.assertEqual(reply, expected_reply)
        reply = parser._parse_file_per_type("cfg", test_files_location + "/test.ini")
        self.assertEqual(reply, expected_reply)

    def test_parser__parse_file_per_type_xml(self):
        parser = ParseIt(config_folder_location=test_files_location)
        reply = parser._parse_file_per_type("xml", test_files_location + "/test.xml")
        expected_reply = {
            'xml_root': {
                'file_type': 'xml',
                'test_bool_false': 'false',
                'test_bool_true': 'true',
                'test_float': '123.123',
                'test_int': '123',
                'test_xml': {
                    'test_xml_key': 'test_xml_value'
                },
                'test_list': {
                    'element': [
                        'test1',
                        'test2',
                        'test3'
                    ]
                },
                'test_string': 'testing'
            }
        }
        self.assertEqual(reply, expected_reply)

    def test_command_line_args_read_command_line_arg(self):
        testargs = ["parse_it_mock_script.py", "--test_key", "test_value"]
        with mock.patch('sys.argv', testargs):
            reply = read_command_line_arg("test_key")
            self.assertEqual(reply, "test_value")

    def test_command_line_args_read_command_line_arg_not_defined(self):
        testargs = ["parse_it_mock_script.py", "--test_key", "test_value"]
        with mock.patch('sys.argv', testargs):
            reply = read_command_line_arg("non_existing_test_key")
            self.assertIsNone(reply)

    def test_command_line_args_command_line_arg_defined_false(self):
        testargs = ["parse_it_mock_script.py", "--test_key", "test_value"]
        with mock.patch('sys.argv', testargs):
            reply = command_line_arg_defined("non_existing_test_key")
            self.assertFalse(reply)

    def test_command_line_args_command_line_arg_defined_true(self):
        testargs = ["parse_it_mock_script.py", "--test_key", "test_value"]
        with mock.patch('sys.argv', testargs):
            reply = command_line_arg_defined("test_key")
            self.assertTrue(reply)

    def test_parser_read_configuration_from_cli_arg(self):
        testargs = ["parse_it_mock_script.py", "--test_cli_key", "test_value", "--test_cli_int", "123"]
        with mock.patch('sys.argv', testargs):
            parser = ParseIt()
            reply = parser.read_configuration_variable("test_cli_key")
            self.assertEqual(reply, "test_value")
            reply = parser.read_configuration_variable("test_cli_int")
            self.assertEqual(reply, 123)
