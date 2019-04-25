import argparse


def read_command_line_arg(argument):
    """Read an environment variable .

            Arguments:
                argument -- name of the argument to get the value of
            Returns:
                the value of the argument, None if doesn't exist
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--" + argument, default=None)
    args = parser.parse_args()
    return getattr(args, argument)
