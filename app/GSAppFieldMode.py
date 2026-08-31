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

# Field Settings panel tooltips, keyed by usage mode, explaining what each
# mode does to the field's column both in the algorithm and in the UI.
FIELD_MODE_TOOLTIPS: dict[GSAppFieldMode, str] = {
    GSAppFieldMode.Ignore: (
        "This field is not used by the algorithm and is hidden from the "
        "participants table."
    ),
    GSAppFieldMode.Keep: (
        "This field is not used by the algorithm, but is still shown in "
        "the participants table and included in exports."
    ),
    GSAppFieldMode.Label: (
        "This field is only used as a display label for participants "
        "(e.g. a name). It has no effect on the allocation."
    ),
    GSAppFieldMode.Diversify: (
        "The algorithm tries to spread this field's distinct values as "
        "evenly as possible across every group."
    ),
    GSAppFieldMode.Cluster: (
        "Participants sharing the same value of this field are kept "
        "together in the same group (e.g. seated at the same table)."
    ),
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
