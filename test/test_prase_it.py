from unittest import TestCase
from parse_it import ParseIt
from parse_it.command_line_args.command_line_args import *
from parse_it.envvars.envvars import *
from parse_it.file.toml import *
from parse_it.file.yaml import *
from parse_it.file.json import *
from parse_it.file.ini import *
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
]

test_files_location = os.getenv("TEST_FILES_LOCATION", "test_files")

class BaseTests(TestCase):

    def test_command_line_args_empty(self):
        reply = read_command_line_arg("empty_variable")
        self.assertIsNone(reply)

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

    def test_file_reader_folder_exists(self):
        reply = folder_exists(test_files_location)
        self.assertTrue(reply)

    def test_file_reader_folder_does_not_exists(self):
        reply = folder_exists("totally_bogus_directory")
        self.assertFalse(reply)

    def test_file_reader_strip_trailing_slash(self):
        reply = strip_trailing_slash(test_files_location + "/")
        self.assertEqual(reply, test_files_location)

    def test_file_reader_strip_trailing_slash_no_strip_needed(self):
        reply = strip_trailing_slash(test_files_location)
        self.assertEqual(reply, test_files_location)

    def test_file_reader_file_types_in_folder(self):
        reply = file_types_in_folder(test_files_location, VALID_FILE_TYPE_EXTENSIONS)
        expected_reply = {
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
            'cfg': [],
            'ini': [
                'test.ini'
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
                'test_list': [
                    '["test1', 'test2', 'test3"]'
                ]
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
        expected_config_files_dict = {'json': ['test.json'], 'yaml': ['test.yaml'], 'yml': [], 'toml': ['test.toml'],
                                      'tml': [], 'conf': [], 'cfg': [], 'ini': ['test.ini']}
        expected_config_type_priority = ['cli_args', 'envvars', 'json', 'yaml', 'yml', 'toml', 'tml', 'conf', 'cfg',
                                         'ini']
        parser = ParseIt(config_type_priority=None, global_default_value=None, type_estimate=True,
                         force_envvars_uppercase=True, config_folder_location=test_files_location, envvar_prefix=None)
        self.assertEqual(parser.config_files_dict, expected_config_files_dict)
        self.assertEqual(parser.config_folder_location, test_files_location)
        self.assertEqual(parser.config_type_priority, expected_config_type_priority)
        self.assertEqual(parser.envvar_prefix, '')
        self.assertTrue(parser.force_envvars_uppercase)
        self.assertIsNone(parser.global_default_value)
        self.assertTrue(parser.type_estimate)

    def test_parser_read_configuration_variable(self):
        parser = ParseIt(config_folder_location=test_files_location)
        reply_json = parser.read_configuration_variable("file_type")
        self.assertEqual(reply_json, "json")
        reply_yaml = parser.read_configuration_variable("test_yaml")
        self.assertEqual(reply_yaml, {'test_yaml_key': 'test_yaml_value'})

    def test_parser_read_configuration_variable_default_value(self):
        parser = ParseIt(config_folder_location=test_files_location)
        reply = parser.read_configuration_variable("file_type123", default_value="test123")
        self.assertEqual(reply, "test123")

    def test_parser_read_configuration_variable_global_default_value(self):
        parser = ParseIt(global_default_value="my_last_resort", config_folder_location=test_files_location)
        reply = parser.read_configuration_variable("this_does_not_exist")
        self.assertEqual(reply, "my_last_resort")

    def test_parser_read_configuration_variable_config_type_priority(self):
        parser = ParseIt(config_type_priority=["yaml", "json"], config_folder_location=test_files_location)
        reply = parser.read_configuration_variable("file_type")
        self.assertEqual(reply, "yaml")
        reply = parser.read_configuration_variable("test_json")
        self.assertEqual(reply, {'test_json_key': 'test_json_value'})

    def test_parser_read_configuration_variable_type_estimate_false(self):
        parser = ParseIt(type_estimate=False, config_folder_location=test_files_location)
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_INT"] = "123"
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_STRING"] = "test"
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_BOOL_TRUE"] = "true"
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_BOOL_FALSE"] = "false"
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_LIST"] = "['test', False, 3]"
        os.environ["TEST_ENVVAR_ESTIMATE_FALSE_DICT"] = "{'string': 'string', 'int': 1}"
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

    def test_parser_read_configuration_variable_type_estimate_true(self):
        parser = ParseIt(type_estimate=True, config_folder_location=test_files_location)
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_INT"] = "123"
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_STRING"] = "test"
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_BOOL_TRUE"] = "true"
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_BOOL_FALSE"] = "false"
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_LIST"] = "[test, False, 3]"
        os.environ["TEST_ENVVAR_ESTIMATE_TRUE_DICT"] = "{'string': 'string', 'int': 1}"
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_TRUE_INT")
        self.assertNotEqual(reply, "123")
        self.assertEqual(reply, 123)
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_FALSE_STRING")
        self.assertEqual(reply, "test")
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_FALSE_BOOL_TRUE")
        self.assertNotEqual(reply, "true")
        self.assertEqual(reply, True)
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_FALSE_BOOL_FALSE")
        self.assertNotEqual(reply, "false")
        self.assertEqual(reply, False)
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_FALSE_LIST")
        self.assertNotEqual(reply, "['test', False, 3]")
        self.assertEqual(reply, ['test', False, 3])
        reply = parser.read_configuration_variable("TEST_ENVVAR_ESTIMATE_FALSE_DICT")
        self.assertNotEqual(reply, "{'string': 'string', 'int': 1}")
        self.assertEqual(reply, {'string': 'string', 'int': 1})

    def test_parser_read_configuration_variable_force_envvars_uppercase_true(self):
        parser = ParseIt(force_envvars_uppercase=True, config_folder_location=test_files_location)
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
        reply_yaml = parser.read_configuration_variable("test_yaml")
        self.assertEqual(reply_yaml, {'test_yaml_key': 'test_yaml_value'})

    def test_parser_read_configuration_variable_envvar_prefix(self):
        parser = ParseIt(envvar_prefix="prefix_test_", config_folder_location=test_files_location)
        os.environ["PREFIX_TEST_TEST_ENVVAR_ESTIMATE_TRUE_INT"] = "123"
        reply = parser.read_configuration_variable("test_envvar_estimate_true_int")
        self.assertEqual(reply, 123)
