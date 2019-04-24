from unittest import TestCase
from parse_this import ParseThis
from parse_this.command_line_args.command_line_args import *
from parse_this.envvars.envvars import *
from parse_this.file.toml import *
from parse_this.file.yaml import *
from parse_this.file.json import *
from parse_this.file.ini import *
from parse_this.file.file_reader import *
from parse_this.type_estimate.type_estimate import *

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
        reply = read_file("test_files/test_read_file")
        self.assertEqual(reply, "it_reads!")

    def test_file_reader_folder_exists(self):
        reply = folder_exists("test_files")
        self.assertTrue(reply)

    def test_file_reader_folder_does_not_exists(self):
        reply = folder_exists("totally_bogus_directory")
        self.assertFalse(reply)

    def test_file_reader_strip_trailing_slash(self):
        reply = strip_trailing_slash("test_files/")
        self.assertEqual(reply, "test_files")

    def test_file_reader_strip_trailing_slash_no_strip_needed(self):
        reply = strip_trailing_slash("test_files")
        self.assertEqual(reply, "test_files")

    def test_file_reader_file_types_in_folder(self):
        reply = file_types_in_folder("test_files", VALID_FILE_TYPE_EXTENSIONS)
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
        reply = parse_ini_file("test_files/test.ini")
        expected_reply = {
            'DEFAULT': {
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
        reply = parse_json_file("test_files/test.json")
        expected_reply = {
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
        reply = parse_toml_file("test_files/test.toml")
        expected_reply = {
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
        reply = parse_yaml_file("test_files/test.yaml")
        expected_reply = {
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

    def test_type_estimate(self):
        pass

    def test_parser_init(self):
        pass

    def test_parser_read_configuration_variable(self):
        pass
