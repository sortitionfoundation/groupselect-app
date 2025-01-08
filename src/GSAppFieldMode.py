from enum import Enum

from groupselect import FieldMode


class GSAppFieldMode(Enum):
    Ignore = 0
    Diversify = 1
    Cluster = 2
    Display = 4
    Label = 5


def map_field_modes(field_mode: GSAppFieldMode):
    if field_mode == GSAppFieldMode.Diversify:
        return FieldMode.Diversify
    elif field_mode == GSAppFieldMode.Cluster:
        return FieldMode.Cluster
    else:
        return FieldMode.Ignore
