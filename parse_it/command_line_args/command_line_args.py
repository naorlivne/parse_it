import sys
from typing import Optional


def read_command_line_arg(argument: str) -> Optional[str]:
    """Read an command line argument.

            Arguments:
                argument -- name of the argument to get the value of
            Returns:
                the value of the argument, None if doesn't exist
    """
    if command_line_arg_defined(argument) is True:
        arg_list = sys.argv
        key_index = arg_list.index("--" + argument) + 1
        reply = arg_list[key_index]
    else:
        reply = None
    return reply


def command_line_arg_defined(argument: str) -> bool:
    """Check if a command line argument is defined.

            Arguments:
                argument -- name of the envvar to get the value of
            Returns:
                True if argument is declared, False otherwise
    """

    if "--" + argument in sys.argv:
        return True
    else:
        return False
