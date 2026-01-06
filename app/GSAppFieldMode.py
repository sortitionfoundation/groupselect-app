from enum import Enum

from groupselect import FieldMode


class GSAppFieldMode(Enum):
    Ignore = 0
    Diversify_rank_1 = 1
    Diversify_rank_2 = 2
    Diversify_rank_3 = 3
    Cluster = 4
    Display = 5
    Label = 6


def map_field_modes(field_mode: GSAppFieldMode):
    if field_mode == GSAppFieldMode.Diversify:
        return FieldMode.Diversify
    elif field_mode == GSAppFieldMode.Cluster:
        return FieldMode.Cluster
    else:
        return FieldMode.Ignore
