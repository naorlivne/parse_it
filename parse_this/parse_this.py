class parse_this:

    def __init__(self):
        # TODO - init the list order with default order of cli_args>envvars>json>yaml>yml>toml>tml>cfg>ini>default_value>global_default_value
        # TODO - have a editable global_default_value of None
        # TODO - have trigger to auto upper case envvars that's true by default
        # TODO - have a trigger to guesstimate the envvars, ini files & cli args types
        # TODO - have a location to look for config files be definable by the user with default location to current folder
        # TODO - narrow down the possible list to only files that exist in the desired location
        # TODO - have the user ability to have only the highest priority type take affect for all config variables rather then on a per variable basis
        # TODO - have option to have prefix for all envvars
        pass

    # TODO - add function which when called looks in order for the configuration variable in all possible locations
