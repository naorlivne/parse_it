import argparse
import sys


def read_command_line_arg(argument):
    """Read an command line argument.

            Arguments:
                argument -- name of the argument to get the value of
            Returns:
                the value of the argument, None if doesn't exist
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--" + argument, default=None)
    args = parser.parse_args()
    return getattr(args, argument)


def command_line_arg_defined(argument):
    """Read an command line argument.

            Arguments:
                argument -- name of the envvar to get the value of
            Returns:
                True if argument is declared, False otherwise
    """

    if argument in sys.argv:
        return True
    else:
        return False
