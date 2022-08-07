from unittest import TestCase, mock
from parse_it import ParseIt
from parse_it.command_line_args.command_line_args import *
from parse_it.envvars.envvars import *
from parse_it.file.toml import *
from parse_it.file.hcl import *
from parse_it.file.yaml import *
from parse_it.file.json import *
from parse_it.file.env import *
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

test_files_location = os.getenv("TEST_FILES_LOCATION", "test/test_files")


class BaseTests(TestCase):

    maxDiff = None

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

    def test_file_reader_file_or_folder_read_folder(self):
        reply = file_or_folder(test_files_location)
        self.assertEqual(reply, "folder")

    def test_file_reader_file_or_folder_read_file(self):
        reply = file_or_folder(test_files_location + "/test.json")
        self.assertEqual(reply, "file")

    def test_file_reader_file_or_folder_read_no_file(self):
        reply = file_or_folder("/non_existing_path")
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
            parser = ParseIt(config_location="totally_bogus_folder_location", config_type_priority=[
                "yaml",
                "json",
                "env_vars"
            ])
            reply = parser.read_configuration_variable("test_config_folder_non_existing_envvar")
            self.assertEqual(reply, "TEST_CONFIG_FOLDER_NON_EXISTING_ENVVAR")

    def test_read_envvar_single_file_config(self):
        os.environ["FILE_TYPE"] = "envvar"
        parser = ParseIt(config_location=test_files_location + "/test.hcl")
        reply = parser.read_configuration_variable("file_type")
        self.assertEqual(reply, "envvar")
        del os.environ["FILE_TYPE"]

    def test_read_cli_args_folder_does_not_exist_raise_warn(self):
        with self.assertWarns(Warning):
            ParseIt(config_location="totally_bogus_folder_location", config_type_priority=[
                "yaml",
                "json",
                "cli_args"
            ])
            test_args = ["parse_it_mock_script.py", "--test_cli_key_no_folder", "test_value"]
            with mock.patch('sys.argv', test_args):
                parser = ParseIt()
                reply = parser.read_configuration_variable("test_cli_key_no_folder")
                self.assertEqual(reply, "test_value")

    def test_file_reader_file_types_in_folder(self):
        reply = file_types_in_folder(test_files_location, VALID_FILE_TYPE_EXTENSIONS)
        expected_reply = {
            'json': [
                'test.json',
                'test_none_values.json',
                'test_subfolder_1/test_sub_subfolder_2/test_subfolder_2.json',
                'test_subfolder_1/test_sub_subfolder_3/test_subfolder_3.json',
                'test_subfolder_1/test_sub_subfolder_3/test_subfolder_4.json',
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
        self.assertDictEqual(reply, expected_reply)

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
        self.assertDictEqual(reply, expected_reply)

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
        self.assertDictEqual(reply, expected_reply)

    def test_env_file(self):
        reply = parse_env_file(test_files_location + "/test.env")
        expected_reply = {
            'file_type': 'env',
            'test_string': 'testing',
            'test_bool_true': 'true',
            'test_bool_false': 'false',
            'test_int': '123',
            'test_float': '123.123',
            'test_list': '["test1","test2","test3"]',
            'test_env': '{"test_env_key": "test_env_value"}'}
        self.assertDictEqual(reply, expected_reply)

    def test_hcl(self):
        reply = parse_hcl_file(test_files_location + "/test.hcl")
        expected_reply = {
            'file_type': "hcl",
            'test_string': 'testing',
            'test_bool_true': True,
            'test_bool_false': False,
            'test_int': 123,
            'test_float': 123.123,
            'test_dict': {
                "hcl_dict_key": "hcl_dict_value"
            },
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
        self.assertDictEqual(reply, expected_reply)

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
        self.assertDictEqual(reply, expected_reply)

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
        self.assertDictEqual(reply, expected_reply)

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
        self.assertDictEqual(reply, expected_reply)

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
        self.assertListEqual(reply, ["test1", "test2", "test3"])
        reply = estimate_type('["test1", {"test_key": "test_value"}, "test3", None]')
        self.assertListEqual(reply, ["test1", {"test_key": "test_value"}, "test3", None])

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

    def test_type_estimate_none_custom(self):
        allowed_none_values = {"null", "none"}
        reply_empty = estimate_type("", allowed_none_values)
        reply_lowercase = estimate_type("none", allowed_none_values)
        reply_null = estimate_type("null", allowed_none_values)
        reply_uppercase = estimate_type("NONE", allowed_none_values)
        reply_mixed = estimate_type("None", allowed_none_values)
        self.assertNotEqual(reply_empty, None)
        self.assertEqual(reply_lowercase, None)
        self.assertEqual(reply_null, None)
        self.assertEqual(reply_uppercase, None)
        self.assertEqual(reply_mixed, None)

    def test_parser_init_no_recurse(self):
        expected_config_files_dict = {
            'env': [
                "test.env"
            ],
            'json': [
                'test.json',
                'test_none_values.json'
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
        expected_config_type_priority = ['cli_args', 'env_vars', "env", 'json', 'yaml', 'yml', 'toml', 'tml', 'hcl',
                                         'tf', 'conf', 'cfg', 'ini', 'xml']
        parser = ParseIt(config_type_priority=None, global_default_value=None, type_estimate=True,
                         force_envvars_uppercase=True, config_location=test_files_location, envvar_prefix=None)
        self.assertDictEqual(parser.config_files_dict, expected_config_files_dict)
        self.assertEqual(parser.config_location, test_files_location)
        self.assertListEqual(parser.config_type_priority, expected_config_type_priority)
        self.assertEqual(parser.envvar_prefix, '')
        self.assertTrue(parser.force_envvars_uppercase)
        self.assertIsNone(parser.global_default_value)
        self.assertTrue(parser.type_estimate)

    def test_parser_init_recurse(self):
        expected_config_files_dict = {
            'env': [
                'test.env'
            ],
            'json': [
                'test.json',
                'test_none_values.json',
                'test_subfolder_1/test_sub_subfolder_2/test_subfolder_2.json',
                'test_subfolder_1/test_sub_subfolder_3/test_subfolder_3.json',
                'test_subfolder_1/test_sub_subfolder_3/test_subfolder_4.json',
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
        expected_config_type_priority = ['cli_args', 'env_vars', 'env', 'json', 'yaml', 'yml', 'toml', 'tml', 'hcl',
                                         'tf', 'conf', 'cfg', 'ini', 'xml']
        parser = ParseIt(config_type_priority=None, global_default_value=None, type_estimate=True, recurse=True,
                         force_envvars_uppercase=True, config_location=test_files_location, envvar_prefix=None)
        self.assertDictEqual(parser.config_files_dict, expected_config_files_dict)
        self.assertEqual(parser.config_location, test_files_location)
        self.assertListEqual(parser.config_type_priority, expected_config_type_priority)
        self.assertEqual(parser.envvar_prefix, '')
        self.assertTrue(parser.force_envvars_uppercase)
        self.assertIsNone(parser.global_default_value)
        self.assertTrue(parser.type_estimate)

    def test_parser_init_single_file(self):
        expected_config_files_dict = {
            'env': [],
            'cfg': [],
            'conf': [],
            'hcl': [],
            'ini': [],
            'json': [
                'test/test_files/test.json'
            ],
            'tf': [],
            'tml': [],
            'toml': [],
            'xml': [],
            'yaml': [],
            'yml': []
        }
        expected_config_type_priority = ['cli_args', 'env_vars', 'env', 'json', 'yaml', 'yml', 'toml', 'tml', 'hcl',
                                         'tf', 'conf', 'cfg', 'ini', 'xml']
        parser = ParseIt(config_type_priority=None, global_default_value=None, type_estimate=True,
                         force_envvars_uppercase=True, config_location=test_files_location + "/test.json",
                         envvar_prefix=None)
        self.assertDictEqual(parser.config_files_dict, expected_config_files_dict)
        self.assertEqual(parser.config_location, test_files_location + "/test.json")
        self.assertListEqual(parser.config_type_priority, expected_config_type_priority)
        self.assertEqual(parser.envvar_prefix, '')
        self.assertTrue(parser.force_envvars_uppercase)
        self.assertIsNone(parser.global_default_value)
        self.assertTrue(parser.type_estimate)

    def test_parser_init_envvar_divider_none(self):
        parser = ParseIt(config_location=test_files_location + "/test.json", envvar_divider=None)
        self.assertFalse(parser.nest_envvars)

    def test_parser_init_envvar_divider_set(self):
        test_envvar_divider = "_"
        parser = ParseIt(config_location=test_files_location + "/test.json", envvar_divider=test_envvar_divider)
        self.assertTrue(parser.nest_envvars)
        self.assertEqual(test_envvar_divider, parser.envvar_divider)

    def test_parser_custom_suffix_mapping_set_config_type_priority_not_set_raise_warning(self):
        with self.assertWarns(Warning):
            ParseIt(config_location=test_files_location, custom_suffix_mapping={"yaml": ["custom"]})

    def test_parser_custom_suffix_mapping_set(self):
        parser = ParseIt(config_location=test_files_location, custom_suffix_mapping={"yaml": ["custom"]},
                         config_type_priority=["custom"] + VALID_FILE_TYPE_EXTENSIONS)
        expected_config_type_priority = ["custom"] + VALID_FILE_TYPE_EXTENSIONS
        expected_valid_type_extension = ['env', 'json', 'yaml', 'yml', 'toml', 'tml', 'hcl', 'tf', 'conf', 'cfg', 'ini',
                                         'xml', 'custom']
        expected_suffix_file_type_mapping = {
            'env': [
                'env'
            ],
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
        self.assertListEqual(expected_config_type_priority, parser.config_type_priority)
        self.assertListEqual(expected_valid_type_extension, parser.valid_file_type_extension)
        self.assertDictEqual(expected_suffix_file_type_mapping, parser.suffix_file_type_mapping)

    def test_parser_read_configuration_variable(self):
        parser = ParseIt(config_location=test_files_location)
        reply_json = parser.read_configuration_variable("file_type")
        self.assertEqual(reply_json, "env")
        reply_yaml = parser.read_configuration_variable("test_yaml")
        self.assertDictEqual(reply_yaml, {'test_yaml_key': 'test_yaml_value'})

    def test_parser_read_configuration_subfolder(self):
        parser = ParseIt(config_location=test_files_location, recurse=True)
        reply = parser.read_configuration_variable("test_json_subfolder")
        self.assertTrue(reply)

    def test_parser_read_configuration_recurse_false(self):
        parser = ParseIt(config_location=test_files_location, recurse=False)
        reply = parser.read_configuration_variable("test_json_subfolder")
        expected_config_files_dict = {
            'env': [
                'test.env'
            ],
            'json': [
                'test.json',
                'test_none_values.json'
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
        self.assertDictEqual(parser.config_files_dict, expected_config_files_dict)
        self.assertIsNone(reply)

    def test_parser_read_configuration_single_file(self):
        parser = ParseIt(config_location=test_files_location + "/test.hcl")
        reply = parser.read_configuration_variable("file_type")
        expected_reply = "hcl"
        self.assertEqual(reply, expected_reply)

    def test_parser_read_configuration_variable_default_value(self):
        parser = ParseIt(config_location=test_files_location)
        reply = parser.read_configuration_variable("file_type123", default_value="test123")
        self.assertEqual(reply, "test123")

    def test_parser_read_configuration_variable_required_true_value_not_given(self):
        parser = ParseIt(config_location=test_files_location)
        with self.assertRaises(ValueError):
            parser.read_configuration_variable("file_type123", required=True)

    def test_parser_config_type_priority_wrong_type_given(self):
        with self.assertRaises(ValueError):
            parser = ParseIt(config_type_priority=['non_existing_type', 'json'])
            parser.read_configuration_variable("file_type123", required=True)

    def test_parser_read_configuration_variable_required_true_value_given_file(self):
        parser = ParseIt(config_location=test_files_location)
        reply_json = parser.read_configuration_variable("file_type", required=True)
        self.assertEqual(reply_json, "env")

    def test_parser_read_configuration_variable_required_true_value_given_envvar(self):
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_INT"] = "123"
        parser = ParseIt(config_location=test_files_location)
        reply_json = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_INT", required=True)
        self.assertEqual(reply_json, 123)

    def test_parser_read_configuration_variable_global_default_value(self):
        parser = ParseIt(global_default_value="my_last_resort", config_location=test_files_location)
        reply = parser.read_configuration_variable("this_does_not_exist")
        self.assertEqual(reply, "my_last_resort")

    def test_parser_read_configuration_variable_config_type_priority(self):
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_INT"] = "123"
        parser = ParseIt(config_type_priority=["yaml", "toml", "ini", "json", "envvars", "env"],
                         config_location=test_files_location)
        reply = parser.read_configuration_variable("file_type")
        self.assertEqual(reply, "yaml")
        reply = parser.read_configuration_variable("test_toml")
        self.assertDictEqual(reply, {'test_toml_key': 'test_toml_value'})
        reply = parser.read_configuration_variable("test_ini")
        self.assertDictEqual(reply, {'test_ini_key': 'test_ini_value'})
        reply = parser.read_configuration_variable("test_json")
        self.assertDictEqual(reply, {'test_json_key': 'test_json_value'})
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_INT")
        self.assertEqual(reply, 123)
        reply = parser.read_configuration_variable("test_list")
        self.assertEqual(reply, ['test1', 'test2', 'test3'])

    def test_parser_read_configuration_variable_type_estimate_false(self):
        parser = ParseIt(type_estimate=False, config_location=test_files_location)
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
        parser = ParseIt(type_estimate=True, config_location=test_files_location)
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
        self.assertListEqual(reply, ['test', False, 3])
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_DICT")
        self.assertNotEqual(reply, "{'string': 'string', 'int': 1}")
        self.assertDictEqual(reply, {'string': 'string', 'int': 1})
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_RECURSIVE_LIST")
        self.assertNotEqual(reply, "['test', False, 3, ['test', True, 35, {'test': 12}]]")
        self.assertListEqual(reply, ['test', False, 3, ['test', True, 35, {'test': 12}]])
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_RECURSIVE_DICT")
        self.assertNotEqual(reply, "{'string': 'string', 'int': 1, 'dict': {'test': [1, 2]}}")
        self.assertDictEqual(reply, {'string': 'string', 'int': 1, 'dict': {'test': [1, 2]}})

    def test_parser_read_configuration_variable_force_envvars_uppercase_true(self):
        parser = ParseIt(force_envvars_uppercase=True)
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_INT"] = "123"
        os.environ["test_envvar_estimate_true_int"] = "456"
        reply = parser.read_configuration_variable("test_envvar_estimate_true_int")
        self.assertEqual(reply, 123)
        self.assertNotEqual(reply, 456)

    def test_parser_read_configuration_variable_force_envvars_uppercase_false(self):
        parser = ParseIt(force_envvars_uppercase=False, config_location=test_files_location)
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_INT"] = "123"
        os.environ["test_envvar_estimate_true_int"] = "456"
        reply = parser.read_configuration_variable("test_envvar_estimate_true_int")
        self.assertNotEqual(reply, 123)
        self.assertEqual(reply, 456)

    def test_parser_read_configuration_variable_config_location(self):
        parser = ParseIt(config_location=test_files_location)
        reply_json = parser.read_configuration_variable("file_type")
        self.assertEqual(reply_json, "env")
        reply_json = parser.read_configuration_variable("test_float")
        self.assertEqual(reply_json, 123.123)
        reply_yaml = parser.read_configuration_variable("test_yaml")
        self.assertDictEqual(reply_yaml, {'test_yaml_key': 'test_yaml_value'})
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
        self.assertDictEqual(reply_xml, expected_reply_xml)
        reply_hcl = parser.read_configuration_variable("test_hcl")
        expected_reply_hcl = {
            'test_hcl_name': {
                'test_hcl_key': 'test_hcl_value'
            }
        }
        self.assertDictEqual(reply_hcl, expected_reply_hcl)

    def test_parser_read_configuration_variable_envvar_prefix(self):
        parser = ParseIt(envvar_prefix="prefix_test_", config_location=test_files_location)
        os.environ["PREFIX_TEST_TEST_ENVVAR_ESTIMATE_TRUE_INT"] = "123"
        reply = parser.read_configuration_variable("test_envvar_estimate_true_int")
        self.assertEqual(reply, 123)

    def test_parser_read_configuration_variable_envvar_nested(self):
        parser = ParseIt(config_location=test_files_location, envvar_divider="_")
        os.environ["TEST_ENVVAR_NESTED"] = "123"
        reply = parser.read_configuration_variable("test_envvar_nested")
        self.assertDictEqual(reply, {"test": {"envvar": {"nested": 123}}})

    def test_envvar_defined_true(self):
        os.environ["TEST_ENV"] = "123"
        reply = envvar_defined("TEST_ENV")
        self.assertTrue(reply)
        del os.environ["TEST_ENV"]

    def test_envvar_defined_false(self):
        reply = envvar_defined("TEST_ENV")
        self.assertFalse(reply)

    def test_envvar_defined_true_upper_case(self):
        os.environ["TEST_ENV"] = "123"
        reply = envvar_defined("test_env", force_uppercase=True)
        self.assertTrue(reply)
        del os.environ["TEST_ENV"]

    def test_envvar_defined_false_upper_case(self):
        os.environ["TEST_ENV"] = "123"
        reply = envvar_defined("test_env", force_uppercase=False)
        self.assertFalse(reply)
        del os.environ["TEST_ENV"]

    def test_read_all_envvars_to_dict_force_uppercase_true(self):
        test_envvars = {"TEST_ENV": "123", "test_env_lowercase": "456"}
        with mock.patch.dict(os.environ, test_envvars):
            reply = read_all_envvars_to_dict(force_uppercase=True)
            self.assertEqual(type(reply), dict)
            self.assertEqual(reply["test_env"], "123")
            self.assertEqual(reply["test_env_lowercase"], "456")

    def test_read_all_envvars_to_dict_force_uppercase_false(self):
        test_envvars = {"TEST_ENV": "123", "test_env_lowercase": "456"}
        with mock.patch.dict(os.environ, test_envvars):
            reply = read_all_envvars_to_dict(force_uppercase=False)
            self.assertEqual(type(reply), dict)
            self.assertEqual(reply["TEST_ENV"], "123")
            self.assertEqual(reply["test_env_lowercase"], "456")

    def test_envvars_split_force_uppercase_false(self):
        expected_reply = {'dict': {'subdict': {'key': 'example_value'}}}
        test_key = "dict_subdict_key"
        test_value = "example_value"
        reply = split_envvar(test_key, test_value, divider="_")
        self.assertEqual(expected_reply, reply)

    def test_envvars_split_force_uppercase_true(self):
        expected_reply = {'dict': {'subdict': {'key': 'example_value'}}}
        test_key = "dict_subdict_key"
        test_value = "example_value"
        reply = split_envvar(test_key, test_value, divider="_")
        self.assertEqual(expected_reply, reply)

    def test_envvars_split_no_nesting_needed(self):
        expected_reply = {'dict': 'example_value'}
        test_key = "dict"
        test_value = "example_value"
        reply = split_envvar(test_key, test_value, divider="_")
        self.assertEqual(expected_reply, reply)

    def test_envvars_split_custom_divider(self):
        expected_reply = {'dict': {'subdict': {'key': 'example_value'}}}
        test_key = "dict.subdict.key"
        test_value = "example_value"
        reply = split_envvar(test_key, test_value, divider=".")
        self.assertEqual(expected_reply, reply)

    def test_envvars_split_envvar_combained_dict(self):
        test_envvars = {"TEST_SPLIT_UPPERCASE1": "test123", "test_split_lowercase1": "test456"}
        with mock.patch.dict(os.environ, test_envvars):
            reply = split_envvar_combained_dict()
            self.assertEqual(type(reply), dict)
            self.assertEqual(reply["test"]["split"]["uppercase1"], "test123")
            self.assertEqual(reply["test"]["split"]["lowercase1"], "test456")

    def test_envvars_split_envvar_combained_dict_custom_divider(self):
        test_envvars = {"TEST.SPLIT.UPPER_CASE2": "test123", "test.split.lower_case2": "test456"}
        with mock.patch.dict(os.environ, test_envvars):
            reply = split_envvar_combained_dict(divider=".")
            self.assertEqual(type(reply), dict)
            self.assertEqual(reply["test"]["split"]["upper_case2"], "test123")
            self.assertEqual(reply["test"]["split"]["lower_case2"], "test456")

    def test_envvars_split_envvar_combained_dict_force_uppercase_false(self):
        test_envvars = {
            "TEST_SPLIT_UPPERCASE3": "test123",
            "test_split_lowercase3": "test456",
            "test_split_lowercase4": "test789"
        }
        with mock.patch.dict(os.environ, test_envvars):
            reply = split_envvar_combained_dict(force_uppercase=False)
            self.assertEqual(type(reply), dict)
            self.assertEqual(reply["TEST"]["SPLIT"]["UPPERCASE3"], "test123")
            self.assertEqual(reply["test"]["split"]["lowercase3"], "test456")
            self.assertEqual(reply["test"]["split"]["lowercase4"], "test789")

    def test_parser_config_found_in_key(self):
        parser = ParseIt(config_location=test_files_location)
        config_found_reply, config_value_reply = parser._check_config_in_dict("test_key", {"test_key": "test_value"})
        self.assertTrue(config_found_reply)
        self.assertEqual(config_value_reply, "test_value")

    def test_parser_config_found_in_key_false(self):
        parser = ParseIt(config_location=test_files_location)
        config_found_reply, config_value_reply = parser._check_config_in_dict("wrong_key", {"test_key": "test_value"})
        self.assertFalse(config_found_reply)
        self.assertEqual(config_value_reply, None)

    def test_parser__parse_file_per_type_wrong_type(self):
        parser = ParseIt(config_location=test_files_location)
        with self.assertRaises(ValueError):
            parser._parse_file_per_type("non_existing_type", test_files_location + "/test.json")

    def test_parser__parse_file_per_type_json(self):
        parser = ParseIt(config_location=test_files_location)
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
        self.assertDictEqual(reply, expected_reply)

    def test_parser__parse_file_per_type_yaml(self):
        parser = ParseIt(config_location=test_files_location)
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
        self.assertDictEqual(reply, expected_reply)
        reply = parser._parse_file_per_type("yml", test_files_location + "/test.yaml")
        self.assertDictEqual(reply, expected_reply)

    def test_parser__parse_file_per_type_custom_yaml(self):
        parser = ParseIt(config_location=test_files_location, custom_suffix_mapping={"yaml": ["custom"]},
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
        self.assertDictEqual(reply, expected_reply)

    def test_parser__parse_file_per_type_toml(self):
        parser = ParseIt(config_location=test_files_location)
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
        self.assertDictEqual(reply, expected_reply)
        reply = parser._parse_file_per_type("tml", test_files_location + "/test.toml")
        self.assertDictEqual(reply, expected_reply)

    def test_parser__parse_file_per_type_hcl(self):
        parser = ParseIt(config_location=test_files_location)
        reply = parser._parse_file_per_type("hcl", test_files_location + "/test.hcl")
        expected_reply = {
            'file_type': 'hcl',
            'test_string': 'testing',
            'test_bool_true': True,
            'test_bool_false': False,
            'test_int': 123,
            'test_float': 123.123,
            'test_dict': {
                "hcl_dict_key": "hcl_dict_value"
            },
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
        self.assertDictEqual(reply, expected_reply)
        reply = parser._parse_file_per_type("tf", test_files_location + "/test.hcl")
        self.assertDictEqual(reply, expected_reply)

    def test_parser__parse_file_per_type_ini(self):
        parser = ParseIt(config_location=test_files_location)
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
        self.assertDictEqual(reply, expected_reply)
        reply = parser._parse_file_per_type("conf", test_files_location + "/test.ini")
        self.assertDictEqual(reply, expected_reply)
        reply = parser._parse_file_per_type("cfg", test_files_location + "/test.ini")
        self.assertDictEqual(reply, expected_reply)

    def test_parser__parse_file_per_type_xml(self):
        parser = ParseIt(config_location=test_files_location)
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
        self.assertDictEqual(reply, expected_reply)

    def test_command_line_args_read_command_line_arg(self):
        test_args = ["parse_it_mock_script.py", "--test_key", "test_value"]
        with mock.patch('sys.argv', test_args):
            reply = read_command_line_arg("test_key")
            self.assertEqual(reply, "test_value")

    def test_command_line_args_read_command_line_arg_not_defined(self):
        test_args = ["parse_it_mock_script.py", "--test_key", "test_value"]
        with mock.patch('sys.argv', test_args):
            reply = read_command_line_arg("non_existing_test_key")
            self.assertIsNone(reply)

    def test_command_line_args_command_line_arg_defined_false(self):
        test_args = ["parse_it_mock_script.py", "--test_key", "test_value"]
        with mock.patch('sys.argv', test_args):
            reply = command_line_arg_defined("non_existing_test_key")
            self.assertFalse(reply)

    def test_command_line_args_command_line_arg_defined_true(self):
        test_args = ["parse_it_mock_script.py", "--test_key", "test_value"]
        with mock.patch('sys.argv', test_args):
            reply = command_line_arg_defined("test_key")
            self.assertTrue(reply)

    def test_command_line_args_read_all_cli_args_to_dict(self):
        test_args = ["parse_it_mock_script.py", "--test_key", "test_value", "--another_test", "another_value"]
        expected_reply = {"test_key": "test_value", "another_test": "another_value"}
        with mock.patch('sys.argv', test_args):
            reply = read_all_cli_args_to_dict()
            self.assertEqual(reply, expected_reply)

    def test_command_line_args_read_all_cli_args_to_dict_no_cli_args(self):
        test_args = ["parse_it_mock_script.py"]
        expected_reply = {}
        with mock.patch('sys.argv', test_args):
            reply = read_all_cli_args_to_dict()
            self.assertEqual(reply, expected_reply)

    def test_command_line_args_read_all_cli_args_to_dict_no_cli_args_with_double_dash(self):
        test_args = ["parse_it_mock_script.py", "-wrong_format_test_key", "test_value"]
        expected_reply = {}
        with mock.patch('sys.argv', test_args):
            reply = read_all_cli_args_to_dict()
            self.assertEqual(reply, expected_reply)

    def test_parser_read_configuration_from_cli_arg(self):
        test_args = ["parse_it_mock_script.py", "--test_cli_key", "test_value", "--test_cli_int", "123"]
        with mock.patch('sys.argv', test_args):
            parser = ParseIt()
            reply = parser.read_configuration_variable("test_cli_key")
            self.assertEqual(reply, "test_value")
            reply = parser.read_configuration_variable("test_cli_int")
            self.assertEqual(reply, 123)

    def test_parser_read_configuration_variable_check_allowed_types_None(self):
        parser = ParseIt(config_location=test_files_location)
        reply_json = parser.read_configuration_variable("file_type", allowed_types=None)
        self.assertEqual(reply_json, "env")

    def test_parser_read_configuration_variable_check_allowed_not_in_types_list(self):
        with self.assertRaises(TypeError):
            parser = ParseIt(config_location=test_files_location)
            parser.read_configuration_variable("file_type", allowed_types=[int, list, dict, None, float])

    def test_parser_read_configuration_variable_check_allowed_in_types_list(self):
        parser = ParseIt(config_location=test_files_location)
        reply_json = parser.read_configuration_variable("file_type", allowed_types=[int, str, dict, None, float])
        self.assertEqual(reply_json, "env")

    def test_parser_read_multiple_configuration_variables_works_multiple_list(self):
        expected_reply = {
            'file_type': 'env',
            'test_hcl': {
                'test_hcl_name': {
                    'test_hcl_key': 'test_hcl_value'
                }
            },
            'test_int': 123,
            'test_list': [
                'test1',
                'test2',
                'test3'
            ]
        }
        parser = ParseIt(config_location=test_files_location)
        reply_json = parser.read_multiple_configuration_variables(["file_type", "test_hcl", "test_int", "test_list"])
        self.assertDictEqual(reply_json, expected_reply)

    def test_parser_read_multiple_configuration_variables_default_value(self):
        expected_reply = {
            'file_type': 'env',
            'non_existing_value': 'test'
        }
        parser = ParseIt(config_location=test_files_location)
        reply_json = parser.read_multiple_configuration_variables(["file_type", "non_existing_value"],
                                                                  default_value="test")
        self.assertDictEqual(reply_json, expected_reply)

    def test_parser_read_multiple_configuration_variables_required_true_raise_error(self):
        parser = ParseIt(config_location=test_files_location)
        with self.assertRaises(ValueError):
            parser.read_multiple_configuration_variables(["file_type", "non_existing_value"], required=True)

    def test_parser_read_multiple_configuration_variables_allowed_types_raise_error(self):
        parser = ParseIt(config_location=test_files_location)
        with self.assertRaises(TypeError):
            parser.read_multiple_configuration_variables(["file_type", "non_existing_value"], allowed_types=[int, dict])

    def test_parser_read_all_configuration_variables(self):
        parser = ParseIt(config_location=test_files_location)
        reply = parser.read_all_configuration_variables()
        self.assertEqual(reply["file_type"], "env")
        self.assertEqual(reply["test_string"], "testing")
        self.assertTrue(reply["test_bool_true"])
        self.assertFalse(reply["test_bool_false"])
        self.assertEqual(reply["test_int"], 123)
        self.assertEqual(reply["test_float"], 123.123)
        self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
        self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_nest_envvars(self):
        parser = ParseIt(config_location=test_files_location, envvar_divider="_", force_envvars_uppercase=True)
        test_envvars = {"test_split_nesting1": "test123", "test_split_nesting2": "test456"}
        with mock.patch.dict(os.environ, test_envvars):
            reply = parser.read_all_configuration_variables()
            self.assertDictEqual(reply["test"]["split"], {'nesting1': 'test123', 'nesting2': 'test456'})
            self.assertEqual(reply["file_type"], "env")
            self.assertEqual(reply["test_string"], "testing")
            self.assertTrue(reply["test_bool_true"])
            self.assertFalse(reply["test_bool_false"])
            self.assertEqual(reply["test_int"], 123)
            self.assertEqual(reply["test_float"], 123.123)
            self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
            self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_default_value_given(self):
        parser = ParseIt(config_location=test_files_location)
        reply = parser.read_all_configuration_variables(default_value={"default_value_test": "it_works"})
        self.assertEqual(reply["default_value_test"], "it_works")
        self.assertEqual(reply["file_type"], "env")
        self.assertEqual(reply["test_string"], "testing")
        self.assertTrue(reply["test_bool_true"])
        self.assertFalse(reply["test_bool_false"])
        self.assertEqual(reply["test_int"], 123)
        self.assertEqual(reply["test_float"], 123.123)
        self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
        self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_none_default_value_given(self):
        parser = ParseIt(config_location=test_files_location)
        reply = parser.read_all_configuration_variables(default_value=None)
        self.assertEqual(reply["file_type"], "env")
        self.assertEqual(reply["test_string"], "testing")
        self.assertTrue(reply["test_bool_true"])
        self.assertFalse(reply["test_bool_false"])
        self.assertEqual(reply["test_int"], 123)
        self.assertEqual(reply["test_float"], 123.123)
        self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
        self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_empty_default_value_given(self):
        parser = ParseIt(config_location=test_files_location)
        reply = parser.read_all_configuration_variables(default_value={})
        self.assertEqual(reply["file_type"], "env")
        self.assertEqual(reply["test_string"], "testing")
        self.assertTrue(reply["test_bool_true"])
        self.assertFalse(reply["test_bool_false"])
        self.assertEqual(reply["test_int"], 123)
        self.assertEqual(reply["test_float"], 123.123)
        self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
        self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_required_given(self):
        parser = ParseIt(config_location=test_files_location)
        reply = parser.read_all_configuration_variables(required=["file_type", "test_int"])
        self.assertEqual(reply["file_type"], "env")
        self.assertEqual(reply["test_string"], "testing")
        self.assertTrue(reply["test_bool_true"])
        self.assertFalse(reply["test_bool_false"])
        self.assertEqual(reply["test_int"], 123)
        self.assertEqual(reply["test_float"], 123.123)
        self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
        self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_empty_required_given(self):
        parser = ParseIt(config_location=test_files_location)
        reply = parser.read_all_configuration_variables(required=[])
        self.assertEqual(reply["file_type"], "env")
        self.assertEqual(reply["test_string"], "testing")
        self.assertTrue(reply["test_bool_true"])
        self.assertFalse(reply["test_bool_false"])
        self.assertEqual(reply["test_int"], 123)
        self.assertEqual(reply["test_float"], 123.123)
        self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
        self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_none_required_given(self):
        parser = ParseIt(config_location=test_files_location)
        reply = parser.read_all_configuration_variables(required=None)
        self.assertEqual(reply["file_type"], "env")
        self.assertEqual(reply["test_string"], "testing")
        self.assertTrue(reply["test_bool_true"])
        self.assertFalse(reply["test_bool_false"])
        self.assertEqual(reply["test_int"], 123)
        self.assertEqual(reply["test_float"], 123.123)
        self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
        self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_allowed_types_given(self):
        parser = ParseIt(config_location=test_files_location)
        reply = parser.read_all_configuration_variables(allowed_types={
            "file_type": [
                str,
                bool
            ],
            "test_int": [
                int,
                str
            ]
        })
        self.assertEqual(reply["file_type"], "env")
        self.assertEqual(reply["test_string"], "testing")
        self.assertTrue(reply["test_bool_true"])
        self.assertFalse(reply["test_bool_false"])
        self.assertEqual(reply["test_int"], 123)
        self.assertEqual(reply["test_float"], 123.123)
        self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
        self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_empty_allowed_types_given(self):
        parser = ParseIt(config_location=test_files_location)
        reply = parser.read_all_configuration_variables(allowed_types={})
        self.assertEqual(reply["file_type"], "env")
        self.assertEqual(reply["test_string"], "testing")
        self.assertTrue(reply["test_bool_true"])
        self.assertFalse(reply["test_bool_false"])
        self.assertEqual(reply["test_int"], 123)
        self.assertEqual(reply["test_float"], 123.123)
        self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
        self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_none_allowed_types_given(self):
        parser = ParseIt(config_location=test_files_location)
        reply = parser.read_all_configuration_variables(allowed_types=None)
        self.assertEqual(reply["file_type"], "env")
        self.assertEqual(reply["test_string"], "testing")
        self.assertTrue(reply["test_bool_true"])
        self.assertFalse(reply["test_bool_false"])
        self.assertEqual(reply["test_int"], 123)
        self.assertEqual(reply["test_float"], 123.123)
        self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
        self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_type_estimate_true(self):
        test_envvars = {"TEST_ENV_TYPE_ESTIMATE": "123"}
        with mock.patch.dict(os.environ, test_envvars):
            parser = ParseIt(config_location=test_files_location, type_estimate=True)
            reply = parser.read_all_configuration_variables()
            self.assertEqual(reply["test_env_type_estimate"], 123)

    def test_parser_read_all_configuration_variables_type_estimate_false(self):
        test_envvars = {"TEST_ENV_TYPE_ESTIMATE": "123"}
        with mock.patch.dict(os.environ, test_envvars):
            parser = ParseIt(config_location=test_files_location, type_estimate=False)
            reply = parser.read_all_configuration_variables()
            self.assertEqual(reply["test_env_type_estimate"], "123")

    def test_parser_read_all_configuration_variables_raise_allowed_types_error(self):
        parser = ParseIt(config_location=test_files_location)
        with self.assertRaises(TypeError):
            parser.read_all_configuration_variables(allowed_types={"file_type": [bool, dict]})

    def test_parser_read_all_configuration_variables_raise_required_error(self):
        parser = ParseIt(config_location=test_files_location)
        with self.assertRaises(ValueError):
            parser.read_all_configuration_variables(required=["non_existing_key"])

    def test_parser_read_all_configuration_variables_config_type_in_data_sources_error(self):
        parser = ParseIt(config_type_priority=['non_existing_type', 'json'])
        with self.assertRaises(ValueError):
            parser.read_all_configuration_variables(required=["non_existing_key"])

    def test_parser_read_all_configuration_variables_read_envvars(self):
        test_envvars = {"TEST_ENV_TYPE_ESTIMATE": "123"}
        with mock.patch.dict(os.environ, test_envvars):
            parser = ParseIt(config_location=test_files_location, type_estimate=True)
            reply = parser.read_all_configuration_variables()
            self.assertEqual(reply["test_env_type_estimate"], 123)
            self.assertEqual(reply["file_type"], "env")
            self.assertEqual(reply["test_string"], "testing")
            self.assertTrue(reply["test_bool_true"])
            self.assertFalse(reply["test_bool_false"])
            self.assertEqual(reply["test_int"], 123)
            self.assertEqual(reply["test_float"], 123.123)
            self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
            self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_read_cli_args(self):
        test_args = ["parse_it_mock_script.py", "--test_cli_key_no_folder", "test_value"]
        with mock.patch('sys.argv', test_args):
            parser = ParseIt(config_location=test_files_location, type_estimate=True)
            reply = parser.read_all_configuration_variables()
            self.assertEqual(reply["test_cli_key_no_folder"], "test_value")
            self.assertEqual(reply["file_type"], "env")
            self.assertEqual(reply["test_string"], "testing")
            self.assertTrue(reply["test_bool_true"])
            self.assertFalse(reply["test_bool_false"])
            self.assertEqual(reply["test_int"], 123)
            self.assertEqual(reply["test_float"], 123.123)
            self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
            self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_read_single_file(self):
        parser = ParseIt(config_location=test_files_location + "/test.hcl", type_estimate=True)
        reply = parser.read_all_configuration_variables()
        self.assertEqual(reply["file_type"], "hcl")
        self.assertEqual(reply["test_string"], "testing")
        self.assertTrue(reply["test_bool_true"])
        self.assertFalse(reply["test_bool_false"])
        self.assertEqual(reply["test_int"], 123)
        self.assertEqual(reply["test_float"], 123.123)
        self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
        self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_recursive_false(self):
        parser = ParseIt(config_location=test_files_location, recurse=False)
        reply = parser.read_all_configuration_variables()
        self.assertEqual(reply["file_type"], "env")
        self.assertEqual(reply["test_string"], "testing")
        self.assertTrue(reply["test_bool_true"])
        self.assertFalse(reply["test_bool_false"])
        self.assertEqual(reply["test_int"], 123)
        self.assertEqual(reply["test_float"], 123.123)
        self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
        self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_recursive_true(self):
        parser = ParseIt(config_location=test_files_location, recurse=True)
        reply = parser.read_all_configuration_variables()
        self.assertEqual(reply["file_type"], "env")
        self.assertEqual(reply["test_string"], "testing")
        self.assertTrue(reply["test_bool_true"])
        self.assertTrue(reply["test_json_subfolder"])
        self.assertFalse(reply["test_bool_false"])
        self.assertEqual(reply["test_int"], 123)
        self.assertEqual(reply["test_float"], 123.123)
        self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
        self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])

    def test_parser_read_all_configuration_variables_check_order(self):
        parser = ParseIt(config_location=test_files_location, config_type_priority=["env_vars", "hcl", "json"])
        test_envvars = {"TEST_INT": "12345"}
        with mock.patch.dict(os.environ, test_envvars):
            reply = parser.read_all_configuration_variables()
            self.assertEqual(reply["file_type"], "hcl")
            self.assertEqual(reply["test_string"], "testing")
            self.assertTrue(reply["test_bool_true"])
            self.assertFalse(reply["test_bool_false"])
            self.assertEqual(reply["test_int"], 12345)
            self.assertEqual(reply["test_float"], 123.123)
            self.assertDictEqual(reply["test_dict"], {'hcl_dict_key': 'hcl_dict_value'})
            self.assertListEqual(reply["test_list"], ['test1', 'test2', 'test3'])
            self.assertDictEqual(reply["test_json"], {"test_json_key": "test_json_value"})

    def test_parser_type_estimate_none(self):
        parser = ParseIt(
            config_location=f"{test_files_location}/test_none_values.json")
        reply = parser.read_all_configuration_variables()
        self.assertEqual(reply["empty_string"], None)
        self.assertEqual(reply["none_lower"], None)
        self.assertEqual(reply["none_upper"], None)
        self.assertEqual(reply["none_mixed"], None)
        self.assertEqual(reply["null"], None)

    def test_parser_type_estimate_none_custom(self):
        parser = ParseIt(
            config_location=f"{test_files_location}/test_none_values.json",
            none_values={"null", "none"})
        reply = parser.read_all_configuration_variables()
        self.assertNotEqual(reply["empty_string"], None)
        self.assertEqual(reply["none_lower"], None)
        self.assertEqual(reply["none_upper"], None)
        self.assertEqual(reply["none_mixed"], None)
        self.assertEqual(reply["null"], None)
