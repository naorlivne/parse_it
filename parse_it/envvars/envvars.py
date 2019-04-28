import os


def read_envvar(envvar, force_uppercase=True):
    """Read an environment variable .

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


def envvar_defined(envvar, force_uppercase=True):
    """Read an environment variable .

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
