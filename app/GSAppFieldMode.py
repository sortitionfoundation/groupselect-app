from enum import Enum

from groupselect import FieldMode


class GSAppFieldMode(Enum):
    """Field-usage roles available in the GroupSelect App.

    Extends the library's :class:`~groupselect.FieldMode` concept with two
    display-only roles that have no effect on the allocation algorithm.

    Attributes:
        Ignore: Field is not used during allocation (default for all columns).
        Diversify: Spread participants proportionally across groups.  Mapped
            to :attr:`~groupselect.FieldMode.Diversify` in the library.
        Cluster: Keep participants sharing the target value in the same
            groups.  Mapped to :attr:`~groupselect.FieldMode.Cluster`.
        Display: Not used for allocation; column is shown in the results
            table to help interpret outcomes.  Mapped to
            :attr:`~groupselect.FieldMode.Ignore`.
        Label: Used as the participant identifier (e.g. name column) in
            result views.  Mapped to :attr:`~groupselect.FieldMode.Ignore`.
    """

    Ignore = 0
    Diversify = 1
    Cluster = 2
    Display = 3
    Label = 4


def map_field_modes(field_mode: GSAppFieldMode):
    """Convert an app field mode to the corresponding library FieldMode.

    Args:
        field_mode: The app-level field usage role.

    Returns:
        The corresponding :class:`~groupselect.FieldMode`.
        ``Display`` and ``Label`` both map to ``FieldMode.Ignore``.
    """
    if field_mode == GSAppFieldMode.Diversify:
        return FieldMode.Diversify
    elif field_mode == GSAppFieldMode.Cluster:
        return FieldMode.Cluster
    else:
        return FieldMode.Ignore
