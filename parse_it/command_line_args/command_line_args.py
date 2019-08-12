import sys
from typing import Optional


def read_command_line_arg(argument: str) -> Optional[str]:
    """Read an command line argument.

            Arguments:
                argument -- name of the cli argument to get the value of, will auto append "--" to it
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
                argument -- name of the cli argument to get the value of, will auto append "--" to it
            Returns:
                True if argument is declared, False otherwise
    """

    if "--" + argument in sys.argv:
        return True
    else:
        return False


def read_all_cli_args_to_dict() -> dict:
    """Returns all cli args (that start with --) key/value pairs as a single dict.

            Returns:
                argument_dict -- A dict of all cli arguments key/value pair
        """
    argument_dict = {}
    arg_list = sys.argv
    for argument in arg_list:
        if argument.startswith("--"):
            key_index = arg_list.index(argument) + 1
            argument_dict[argument[2:]] = arg_list[key_index]
    return argument_dict
