"""Field usage modes as used by the app, and their mapping to groupselect."""

from enum import Enum

from groupselect import FieldMode


class GSAppFieldMode(Enum):
    """How a participants' data field is used within the app."""

    Ignore = 0
    Diversify = 1
    Cluster = 2
    Display = 3
    Label = 4


def map_field_modes(field_mode: GSAppFieldMode):
    """Map an app-level field usage mode to a groupselect FieldMode."""
    if field_mode == GSAppFieldMode.Diversify:
        return FieldMode.Diversify
    elif field_mode == GSAppFieldMode.Cluster:
        return FieldMode.Cluster
    else:
        return FieldMode.Ignore
