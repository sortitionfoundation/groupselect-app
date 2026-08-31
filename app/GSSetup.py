"""A named ensemble of allocations, as shown as one item in the Results tab."""

from groupselect import AllocationEnsemble


class GSSetup:
    """One "Setup": a named ensemble, with an explicit name per allocation."""

    def __init__(
        self,
        name: str,
        ensemble: None | AllocationEnsemble = None,
        allocation_names: None | list[str] = None,
    ):
        """Initialise the setup, defaulting the ensemble/names if not given."""
        self.name: str = name
        self.ensemble: AllocationEnsemble = (
            ensemble if ensemble is not None else AllocationEnsemble()
        )
        self.allocation_names: list[str] = (
            allocation_names if allocation_names is not None else []
        )

    def next_allocation_name(self) -> str:
        """Return the next default "Allocation #" name, unique in the setup."""
        return next_unique_name("Allocation", self.allocation_names)

    def add_allocations(self, new_allocations: AllocationEnsemble):
        """Append allocations to the ensemble, each given a default name."""
        for allocation in new_allocations:
            self.allocation_names.append(self.next_allocation_name())
            self.ensemble.append(allocation)


def next_unique_name(prefix: str, existing_names: list[str]) -> str:
    """Return "<prefix> <n>", n starting at len(existing_names) + 1.

    If that name is already taken, n is bumped until a free one is found.
    """
    n = len(existing_names) + 1
    while f"{prefix} {n}" in existing_names:
        n += 1
    return f"{prefix} {n}"
