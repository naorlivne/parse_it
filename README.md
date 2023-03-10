# parse_it

A python library for parsing multiple types of config files, envvars and command line arguments that takes the headache out of setting app configurations.

Github actions CI unit tests & auto PyPi push status: [![CI/CD](https://github.com/naorlivne/parse_it/actions/workflows/full_ci_cd_workflow.yml/badge.svg)](https://github.com/naorlivne/parse_it/actions/workflows/full_ci_cd_workflow.yml)

Code coverage: [![codecov](https://codecov.io/gh/naorlivne/parse_it/branch/master/graph/badge.svg)](https://codecov.io/gh/naorlivne/parse_it)


# Install

First install parse_it, for Python 3.6 & higher this is simply done using pip:

```bash
# Install from PyPi for Python version 3.6 & higher
pip install parse_it
```

If your using a Python 3.4 or older you will require the `typing` backported package as well, this is done with the following optional install:

```bash
# Install from PyPi for Python version 3.4 & lower
pip install parse_it[typing]
```

# How to use

```python

# Load parse_it
from parse_it import ParseIt

# Create parse_it object.
parser = ParseIt()

# Now you can read your configuration values no matter how they are configured (cli args, envvars, json/yaml/etc files)
my_config_key = parser.read_configuration_variable("my_config_key")

```

By default all configuration files will be assumed to be in the workdir but if you want you can also easily set it to look in all subfolders recursively:

```python
# Load parse_it
from parse_it import ParseIt

# cat /etc/my_config_folder/my_inner_conf_folder/my_config.json >>>
#
# {
#   "my_int": 123
# }
# 

# Create parse_it object that will look for the config files in the "/etc/my_config_folder" and all of it's subfolders
parser = ParseIt(config_location="/etc/my_config_folder", recurse=True)
my_config_key = parser.read_configuration_variable("my_int")
# my_config_key will now be an int of 123

```

By default parse_it will look for the configuration options in the following order & will return the first one found:

* `cli_args` - [command line arguments](https://en.wikipedia.org/wiki/Command-line_interface#Arguments) that are passed in the following format ``--key value``
* `env_vars` - [environment variables](https://en.wikipedia.org/wiki/Environment_variable), you can also use `envvars` as an alias for it
* `env` - [.env](https://github.com/theskumar/python-dotenv#usages) formatted files, any file ending with a .env extension in the configuration folder is assumed to be this
* `json` - [JSON](https://en.wikipedia.org/wiki/JSON) formatted files, any file ending with a .json extension in the configuration folder is assumed to be this
* `yaml` - [YAML](https://en.wikipedia.org/wiki/YAML) formatted files, any file ending with a .yaml extension in the configuration folder is assumed to be this
* `yml` - [YAML](https://en.wikipedia.org/wiki/YAML) formatted files, any file ending with a .yml extension in the configuration folder is assumed to be this
* `toml` - [TOML](https://en.wikipedia.org/wiki/TOML) formatted files, any file ending with a .toml extension in the configuration folder is assumed to be this
* `tml` - [TOML](https://en.wikipedia.org/wiki/TOML) formatted files, any file ending with a .tml extension in the configuration folder is assumed to be this
* `hcl` - [HCL](https://github.com/hashicorp/hcl) formatted files, any file ending with a .hcl extension in the configuration folder is assumed to be this
* `tf` - [HCL](https://github.com/hashicorp/hcl) formatted files, any file ending with a .tf extension in the configuration folder is assumed to be this
* `conf` - [INI](https://en.wikipedia.org/wiki/INI_file) formatted files, any file ending with a .conf extension in the configuration folder is assumed to be this
* `cfg` - [INI](https://en.wikipedia.org/wiki/INI_file) formatted files, any file ending with a .cfg extension in the configuration folder is assumed to be this
* `ini` - [INI](https://en.wikipedia.org/wiki/INI_file) formatted files, any file ending with a .ini extension in the configuration folder is assumed to be this
* `xml` - [XML](https://en.wikipedia.org/wiki/XML) formatted files, any file ending with a .xml extension in the configuration folder is assumed to be this
* configuration default value - every configuration value can also optionally be set with a default value
* global default value - the parser object also has a global default value which can be set

if multiple files of the same type exists in the same folder parse_it will look in all of them in alphabetical order before going to the next type, 

You can decide on using your own custom order of any subset of the above options (default values excluded, they will always be last):

```python
# Load parse_it
from parse_it import ParseIt

# Create parse_it object which will only look for envvars then yaml & yml files then json files
parser = ParseIt(config_type_priority=["env_vars", "yaml", "yml", "json"])

```

The global default value by default is None but if needed it's simple to set it:

```python
# Load parse_it
from parse_it import ParseIt

# Create parse_it object with a custom default value
parser = ParseIt()
my_config_key = parser.read_configuration_variable("my_undeclared_key")
# my_config_key will now be a None

# Create parse_it object with a custom default value
parser = ParseIt(global_default_value="my_default_value")
my_config_key = parser.read_configuration_variable("my_undeclared_key")
# my_config_key will now be an string of "my_default_value"

```

parse_it will by default attempt to figure out the type of value returned so even in the case of envvars, cli args & INI files you will get strings/dicts/etc:

```python
# Load parse_it
from parse_it import ParseIt

# This is just for the example
import os
os.environ["MY_INT"] = "123"
os.environ["MY_LIST"] = "['first_item', 'second_item', 'third_item']"
os.environ["MY_DICT"] = "{'key': 'value'}"

# Create parse_it object
parser = ParseIt()
my_config_key = parser.read_configuration_variable("MY_INT")
# my_config_key will now be an string of "123"
my_config_key = parser.read_configuration_variable("MY_LIST")
# my_config_key will now be an list of ['first_item', 'second_item', 'third_item']
my_config_key = parser.read_configuration_variable("MY_DICT")
# my_config_key will now be an dict of {'key': 'value'}

# you can easily disable the type estimation
parser = ParseIt(type_estimate=False)
my_config_key = parser.read_configuration_variable("MY_INT")
# my_config_key will now be an string of "123"
my_config_key = parser.read_configuration_variable("MY_LIST")
# my_config_key will now be an string of "['first_item', 'second_item', 'third_item']"
my_config_key = parser.read_configuration_variable("MY_DICT")
# my_config_key will now be an string of "{'key': 'value'}"

```

As envvars recommended syntax is to have all keys be UPPERCASE which is diffrent then all the rest of the configuration files parse_it will automatically change any needed config value to be in ALL CAPS when looking at envvars for the matching value but if needed you can of course disable that feature: 

```python
# Load parse_it
from parse_it import ParseIt

# This is just for the example
import os
os.environ["MY_STRING"] = "UPPER"
os.environ["my_string"] = "lower"

# Create parse_it object
parser = ParseIt()
my_config_key = parser.read_configuration_variable("my_string")
# my_config_key will now be an string of "UPPER"

# disabling force envvar uppercase
parser = ParseIt(force_envvars_uppercase=False)
my_config_key = parser.read_configuration_variable("my_string")
# my_config_key will now be an string of "lower"

```

You can also easily add a prefix to all envvars (note that `force_envvars_uppercase` will also affect the given prefix):

```python
# Load parse_it
from parse_it import ParseIt

# This is just for the example
import os
os.environ["PREFIX_MY_INT"] = "123"

# add a prefix to all envvars used
parser = ParseIt(envvar_prefix="prefix_")
my_config_key = parser.read_configuration_variable("my_int")
# my_config_key will now be a int of 123

```

You can also set a default value on a per configuration key basis:

```python
# Load parse_it
from parse_it import ParseIt

# get a default value of the key
parser = ParseIt()
my_config_key = parser.read_configuration_variable("my_undeclared_key", default_value="my_value")
# my_config_key will now be a string of "my_value"

```

You can also declare a key to be required (disabled by default) so it will raise a ValueError if not declared by the user anywhere:

```python
# Load parse_it
from parse_it import ParseIt

# will raise an error as the key is not declared anywhere and required is set to True
parser = ParseIt()
my_config_key = parser.read_configuration_variable("my_undeclared_key", required=True)
# Will raise ValueError

```

While generally not a good idea sometimes you can't avoid it and will need to use a custom non standard file suffix, you can add a custom mapping of suffixes to any of the supported file formats as follows (note that `config_type_priority` should also be set to configure the priority of said custom suffix):

```python
# Load parse_it
from parse_it import ParseIt

# Create parse_it object which will only look for envvars then the custom_yaml_suffix then standard yaml & yml files then json files
parser = ParseIt(config_type_priority=["env_vars", "custom_yaml_suffix", "yaml", "yml", "json"], custom_suffix_mapping={"yaml": ["custom_yaml_suffix"]})

```

You might sometimes want to check that the enduser passed to your config a specific type of variable, parse_it allows you to easily check if a value belongs to a given list of types by setting `allowed_types` which will then raise a TypeError if the value type given is not in the list of `allowed_types`, by default this is set to None so no type ensuring takes place:

```python
# Load parse_it
from parse_it import ParseIt

# This is just for the example
import os
os.environ["ONLY_INTGERS_PLEASE"] = "123"

# Create parse_it object which will only look for envvars then the custom_yaml_suffix then standard yaml & yml files then json files
parser = ParseIt()

# skips the type ensuring check as it's not set so all types are accepted
my_config_key = parser.read_configuration_variable("only_intgers_please")

# the type of the variable value is in the list of allowed_types so no errors\warning\etc will be raised
my_config_key = parser.read_configuration_variable("only_intgers_please", allowed_types=[int])

# will raise a TypeError
my_config_key = parser.read_configuration_variable("only_intgers_please", allowed_types=[str, dict, list, None])

```

Sometimes you'll need a lot of configuration keys to have the same parse_it configuration params, rather then looping over them yourself this can be achieved with the `read_multiple_configuration_variables` function that you will give it a list of the configuration keys you want & will apply the same configuration to all and return you a dict with the key/value of the configurations back.

```python
# Load parse_it
from parse_it import ParseIt

# Create parse_it object.
parser = ParseIt()

# Read multiple config keys at once, will return {"my_first_config_key": "default_value", "my_second_config_key": "default_value"} in the example below
my_config_key = parser.read_multiple_configuration_variables(["my_first_config_key", "my_second_config_key"], default_value="default_value", required=False, allowed_types=[str, list, dict, int])

```

You can also read a single file rather then a config directory.

```python
# Load parse_it
from parse_it import ParseIt

# cat /etc/my_config_folder/my_config.json >>>
#
# {
#   "my_int": 123
# }
# 

# Create parse_it object that will look at a single config file, envvars & cli
parser = ParseIt(config_location="/etc/my_config_folder/my_config.json")
my_config_key = parser.read_configuration_variable("my_int")
# my_config_key will now be an int of 123

```

Another option is to read all configurations from all valid sources into a single dict that will include the combined results of all of them (by combined it means it will return only the highest priority of each found key & will combine different keys from different sources into a single dict), this provides less flexibility then reading the configuration variables one by one and is a tad (but just a tad) slower but for some use cases is simpler to use:

```python
# Load parse_it
from parse_it import ParseIt

# Create parse_it object
parser = ParseIt()

my_config_dict = parser.read_all_configuration_variables()
# my_config_dict will now be a dict that includes the keys of all valid sources with the values of each being taken only from the highest priority source

# you can still define the "default_value", "required" & "allowed_types" when reading all configuration variables to a single dict
my_config_dict = parser.read_all_configuration_variables(default_value={"my_key": "my_default_value", "my_other_key": "my_default_value"}, required=["my_required_key","my_other_required_key"], allowed_types={"my_key": [str, list, dict, int], "my_other_key": [str, list, dict, int]})

```

It has also become a common practice to divide envvar keys by a divider character (usually `_`) and nest then as subdicts, this assists in declaring complex dictionaries subkeys with each of them being given it's own key, parse_it supports this option as well by setting the `envvar_divider` variable when declaring the parse_it object (disabled by default):

```python
# Load parse_it
from parse_it import ParseIt

# This is just for the example
import os
os.environ["NEST1_NEST2_NEST3"] = "123"

# Create parse_it object with an envvar_divider
parser = ParseIt(envvar_divider="_")

my_config_dict = parser.read_all_configuration_variables()
# my_config_dict will now be a dict that includes the keys of all valid sources with the values of each being taken only from the highest priority source & the envars keys will be turned to nested subdicts.
# my_config_dict will have in it the following dict {"nest1": {"nest2":{"nest3": 123}}} 

```
You can define which values should be considered None type. Default is `{"", "null", "none"}`

```python
# Load parse_it
from parse_it import ParseIt
# This is just for the example
import os
os.environ["my_config_key1"] = "Nothing"
os.environ["my_config_key2"] = "null"
# Create parse_it object that will only consider "Nothing" and "null" as None type ( defaults to {"", "null", "none"}) 
parser = ParseIt(none_values={"Nothing", "null"})
my_config_key1 = parser.read_configuration_variable("my_config_key1")
my_config_key2 = parser.read_configuration_variable("my_config_key2")
# my_config_key1 and my_config_key2 will now be `None`

```
