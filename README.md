# parse_it

A python library for parsing multiple types of config files, envvars and command line arguments that takes the headache out of setting app configurations.

Travis CI unit tests & auto PyPi push status: [![Build Status](https://travis-ci.org/naorlivne/parse_it.svg?branch=master)](https://travis-ci.org/naorlivne/parse_it)

Code coverage: [![codecov](https://codecov.io/gh/naorlivne/parse_it/branch/master/graph/badge.svg)](https://codecov.io/gh/naorlivne/parse_it)



# Install

First install parse_it:

```bash
# Install from PyPi
pip install parse_it
```

# How to use

```python

# Load parse_it
from parse_it import ParseIt

# Create API object.
parser = ParseIt()

# Now you can read your configuration values no matter how they are configured (cli args, envvars, json/yaml/etc files)
my_config_key = parser.read_configuration_variable("my_config_key")

```

By default all configuration files will be assumed to be in the workdir but that too can be easily changed:

```python
# Load parse_it
from parse_it import ParseIt

# cat /etc/my_config_folder/my_config.json >>>
#
# {
#   "my_int": 123
# }
# 


# Create API object
parser = ParseIt(config_folder_location="/etc/my_config_folder")
my_config_key = parser.read_configuration_variable("my_int")
# my_config_key will now be an int of 123

```

By default parse_it will look for the configuration options in the following order & will return the first one found:

* cli_args - command line arguments that are passed in the following format ``--key value``
* env_vars - environment variables
* envvars - alias for env_vars
* json - JSON formatted files, any file ending with a .json extension in the configuration folder is assumed to be this
* yaml - YAML formatted files, any file ending with a .yaml extension in the configuration folder is assumed to be this
* yml - YAML formatted files, any file ending with a .yml extension in the configuration folder is assumed to be this
* toml - TOML formatted files, any file ending with a .toml extension in the configuration folder is assumed to be this
* tml - TOML formatted files, any file ending with a .tml extension in the configuration folder is assumed to be this
* conf - INI formatted files, any file ending with a .conf extension in the configuration folder is assumed to be this
* cfg - INI formatted files, any file ending with a .cfg extension in the configuration folder is assumed to be this
* ini - - INI formatted files, any file ending with a .ini extension in the configuration folder is assumed to be this
* configuration default value - every configuration value can also optionally be set with a default value
* global default value - - the parser object also has a global default value which can be set

if multiple files of the same type exists in the same folder parse_it will look in all of them before going to the next type, 

You can decide on using your own custom order of any subset of the following options:

```python
# Load parse_it
from parse_it import ParseIt

# Create API object which will only look for envvars then yaml & yml files then json files
parser = ParseIt(config_type_priority=["envvars", "yaml", "yml", "json"])

```

The global default value by default is None but if needed it's simple to set it:

```python
# Load parse_it
from parse_it import ParseIt

# Create API object with a custom default value
parser = ParseIt()
my_config_key = parser.read_configuration_variable("my_undeclared_key")
# my_config_key will now be a None

# Create API object with a custom default value
parser = ParseIt(global_default_value="my_default_value")
my_config_key = parser.read_configuration_variable("my_undeclared_key")
# my_config_key will now be an string of "my_default_value"

```

parse_it will by default attempt to figure out the type of value returned so even in the case of envvars & INI files you will get strings/dicts/etc:

```python
# Load parse_it
from parse_it import ParseIt
import os

# This is just for the example
os.environ["MY_INT"] = "123"

# Create API object
parser = ParseIt()
my_config_key = parser.read_configuration_variable("MY_INT")
# my_config_key will now be an int of 123

# you can easily disable the type estimation
parser = ParseIt(type_estimate=False)
my_config_key = parser.read_configuration_variable("MY_INT")
# my_config_key will now be an string of "123"

```

As envvars recommended syntax is to have all keys be UPPERCASE which is diffrent then all the rest of the configuration files parse_it will automatically change any needed config value to be in ALL CAPS when looking at envvars for the matching value: 

```python
# Load parse_it
from parse_it import ParseIt
import os

# This is just for the example
os.environ["MY_INT"] = "123"

# Create API object
parser = ParseIt()
my_config_key = parser.read_configuration_variable("my_int")
# my_config_key will now be an int of 123

# disabling force envvar uppercase
parser = ParseIt(force_envvars_uppercase=False)
my_config_key = parser.read_configuration_variable("my_int")
# my_config_key will now be a None

```

You can also easily add a prefix to all envvars:

```python
# Load parse_it
from parse_it import ParseIt
import os

# This is just for the example
os.environ["PREFIX_MY_INT"] = "123"

# add a prefix to all envvars used
parser = ParseIt(envvar_prefix="prefix_")
my_config_key = parser.read_configuration_variable("my_int")
# my_config_key will now be a in of 123

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
