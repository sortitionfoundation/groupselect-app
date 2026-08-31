"""Field usage modes as used by the app, and their mapping to groupselect."""

from enum import Enum

from groupselect import FieldMode


class GSAppFieldMode(Enum):
    """How a participants' data field is used within the app.

    Order matches the left-to-right layout of the field-usage lists in the
    Generate tab's Field Settings panel (see `FIELD_MODE_LABELS` below).
    """

    Ignore = 0
    Keep = 1
    Label = 2
    Diversify = 3
    Cluster = 4


# Field Settings panel list titles, keyed by usage mode. Kept alongside the
# enum so the UI label and the underlying mode it drives can't drift apart.
FIELD_MODE_LABELS: dict[GSAppFieldMode, str] = {
    GSAppFieldMode.Ignore: "Ignore and hide:",
    GSAppFieldMode.Keep: "Ignore but display:",
    GSAppFieldMode.Label: "Use as label:",
    GSAppFieldMode.Diversify: "Diversify:",
    GSAppFieldMode.Cluster: "Cluster:",
}


def map_field_modes(field_mode: GSAppFieldMode):
    """Map an app-level field usage mode to a groupselect FieldMode."""
    if field_mode == GSAppFieldMode.Diversify:
        return FieldMode.Diversify
    elif field_mode == GSAppFieldMode.Cluster:
        return FieldMode.Cluster
    elif field_mode == GSAppFieldMode.Keep:
        return FieldMode.Keep
    else:
        return FieldMode.Ignore
