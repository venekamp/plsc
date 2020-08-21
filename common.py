from enum import IntEnum
import ldap


class VerboseLevel(IntEnum):
    """
    Defining the meaning of verbose levels.
    """
    ERROR = 0
    WARNING = 1
    INFO = 2
    DEBUG = 3


class ConfigItemNotFound(Exception):
    """A configuration item could not be found."""
    def __init__(self, config_item):
        self.config_item = config_item


def get_value_from_config(config, *keys):
    """
    Get the value that belongs to the keys combination from the config file.
    This function is called recursively until either the key path delivers a
    value, or the key path is invalid, in which case the ConfigItemNotFound
    exception is raised. Otherwise the found value is returned.
    """

    try:
        if len(keys) == 1:
            return config[keys[0]]
        else:
            return get_value_from_config(config[keys[0]], *keys[1:])
    except KeyError:
        raise ConfigItemNotFound(keys[0])
    except ConfigItemNotFound as e:
        config_item = f'{keys[0]} → {e.config_item}'
        raise ConfigItemNotFound(config_item)
