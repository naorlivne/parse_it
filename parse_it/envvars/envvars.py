import os
import dpath.util
import dpath.options
from typing import Optional, Union


def read_envvar(envvar: str, force_uppercase: bool = True) -> Optional[str]:
    """Read an environment variable, if force_uppercase is true will convert all keys
        to be UPPERCASE

            Arguments:
                envvar -- name of the envvar to get the value of
                force_uppercase -- if the envvar key will be forced to be all in UPPERCASE, defaults to True
            Returns:
                the value of the envvar, None if doesn't exist
    """
    if force_uppercase is True:
        envvar = envvar.upper()
    envvar_value = os.getenv(envvar)

    if isinstance(envvar_value, str) is True:
        # this weird encode and decode is to avoid some cases where envvar get special characters escaped
        envvar_value = envvar_value.encode('latin1').decode('unicode_escape')
    return envvar_value


def envvar_defined(envvar: str, force_uppercase: bool = True) -> bool:
    """Check if an environment variable is defined, if force_uppercase is true will convert all keys
        to be UPPERCASE

            Arguments:
                envvar -- name of the envvar to get the value of
                force_uppercase -- if the envvar key will be forced to be all in UPPERCASE, defaults to True
            Returns:
                True if envvar is declared, False otherwise
    """
    if force_uppercase is True:
        envvar = envvar.upper()

    if envvar in os.environ:
        return True
    else:
        return False


def read_all_envvars_to_dict(force_uppercase: bool = True) -> dict:
    """Read all environment variables and return them in a dict form, if force_uppercase is true will convert all keys
        to be UPPERCASE

            Arguments:
                force_uppercase -- while counter-intuitive in the naming it means that if the environment variable
                    is uppercase the dict will treat it as the same one as a lowercase one & will return it in
                    lowercase form (name saved to match all the other uses of said function)
            Returns:
                envvar_dict -- A dict of all environment variables key/value pairs
    """
    envvar_dict = {}
    for envvar in os.environ:
        if force_uppercase is True:
            envvar_dict[envvar.lower()] = os.environ.get(envvar)
        else:
            envvar_dict[envvar] = os.environ.get(envvar)
    return envvar_dict


def split_envvar(envvar: Union[str, list], value: str, divider: str = "_"):
    """Take an envvar & it's value and split it by the divider to a nested dictionary

                Arguments:
                    envvar -- the envvar key to split into nested dictionary
                    value -- the bottom most value of the nested envvars keys
                    divider -- the string letter by which to divide the envvar key by, defaults to "_"
                Returns:
                    envvar_dict -- A dict that is the result of the envvar being split by the divider with the value
                        appended as the bottom most of the nest key
    """
    if type(envvar) == str:
        envvar_list = envvar.split(divider)
    else:
        envvar_list = envvar

    if len(envvar_list) > 1:
        envvar_dict = {
            envvar_list[0]: split_envvar(envvar_list[1:], value, divider)
        }
    else:
        envvar_dict = {
            envvar_list[0]: value
        }

    return envvar_dict


def split_envvar_combained_dict(divider: str = "_", force_uppercase: bool = True):
    """Returns a dict of all envvars that has had their keys split by the divider into nested dicts

                    Arguments:
                        divider -- the string letter by which to divide the envvar key by, defaults to "_"
                        force_uppercase -- if the envvar key will be forced to be all in UPPERCASE, defaults to True
                    Returns:
                        envvar_split_dict -- A dict that is the result of all envvars being split by the divider with
                            the value appended as the bottom most of the nest key
    """
    envvar_dict = read_all_envvars_to_dict(force_uppercase=force_uppercase)
    envvar_split_dict = {}
    for envvar_key, envvar_value in envvar_dict.items():
        dpath.options.ALLOW_EMPTY_STRING_KEYS=True
        temp_split_envvar = split_envvar(envvar_key, envvar_value, divider=divider)
        dpath.util.merge(envvar_split_dict, temp_split_envvar)
    return envvar_split_dict
