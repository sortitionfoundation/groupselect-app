"""Modal dialog for choosing "Export as..." format, options, and components."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QComboBox,
)

from datahandling import FILE_SEP_OPTIONS, FILE_QUOTE_OPTIONS

from GSExportSettings import GSExportSelection, GSExportSettings
from GSProject import GSProject


# QTreeWidgetItem column-0 data roles identifying what each row represents.
_ROLE_KIND = Qt.ItemDataRole.UserRole
_ROLE_ID = Qt.ItemDataRole.UserRole + 1

KIND_RAW = "raw"
KIND_MAPPED = "mapped"
KIND_TERMS = "terms"
KIND_ALL = "all"
KIND_SETUP = "setup"
KIND_ALLOCATION = "allocation"


class GSExportDialog(QDialog):
    """Dialog for choosing the export format, its options, and components.

    XLSX allows any combination of components (one per sheet), shown as a
    checkable tree with the setups/allocations cascading top-down and
    tristate-aggregating bottom-up. CSV can only ever hold one table, so the
    same tree switches to plain single-row selection instead (with "All"
    disabled, since it can never collapse into one table).
    """

    def __init__(
        self,
        parent: QWidget,
        project: GSProject,
        initial_format: str = "xlsx",
        initial_csv_sep: str = ";",
        initial_csv_quote: str = '"',
        initial_selection: None | GSExportSelection = None,
    ):
        """Build the dialog, pre-filled from the given (or default) state."""
        super(GSExportDialog, self).__init__(parent)
        self.setWindowTitle("Export as...")
        self._project = project
        self._updating = False  # guards against re-entrant itemChanged

        self._setup_items: dict[int, QTreeWidgetItem] = {}
        self._allocation_items: dict[int, QTreeWidgetItem] = {}

        self._create_ui(initial_format)
        self._csv_sep.setCurrentIndex(
            max(self._csv_sep.findData(initial_csv_sep), 0)
        )
        self._csv_quote.setCurrentIndex(
            max(self._csv_quote.findData(initial_csv_quote), 0)
        )

        is_csv = initial_format == "csv"
        self._set_mode(is_csv)
        if initial_selection is not None:
            self._apply_selection(initial_selection, is_csv)
        else:
            self._apply_default_selection(is_csv)

        # Only now start reacting to further, user-driven format changes.
        self._radio_xlsx.toggled.connect(self._format_changed)

    def _create_ui(self, initial_format: str):
        layout = QVBoxLayout()

        format_group = QGroupBox("Format")
        self._radio_xlsx = QRadioButton("Excel workbook (.xlsx)")
        self._radio_csv = QRadioButton("CSV file (.csv)")
        (
            self._radio_xlsx if initial_format == "xlsx" else self._radio_csv
        ).setChecked(True)
        format_layout = QHBoxLayout()
        format_layout.addWidget(self._radio_xlsx)
        format_layout.addWidget(self._radio_csv)
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        self._csv_group = QGroupBox("CSV options")
        self._csv_sep = QComboBox()
        for sep, label in FILE_SEP_OPTIONS.items():
            self._csv_sep.addItem(label, sep)
        self._csv_quote = QComboBox()
        for quote, label in FILE_QUOTE_OPTIONS.items():
            self._csv_quote.addItem(label, quote)
        csv_form = QFormLayout()
        csv_form.addRow(QLabel("Separator"), self._csv_sep)
        csv_form.addRow(QLabel("Quote character"), self._csv_quote)
        self._csv_group.setLayout(csv_form)
        layout.addWidget(self._csv_group)

        layout.addWidget(QLabel("Components to export:"))
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

        # Populate before wiring up change signals, so that building the
        # tree's initial (still-unchecked/unselected) items doesn't touch
        # _update_ok_enabled() before self._buttons exists.
        self._populate_tree()
        self._tree.itemChanged.connect(self._item_changed)
        self._tree.currentItemChanged.connect(
            lambda *args: self._update_ok_enabled()
        )
        layout.addWidget(self._tree)
        layout.addWidget(self._buttons)

        self.setLayout(layout)
        self.resize(420, 480)

    def _populate_tree(self):
        self._item_raw = self._make_item(
            self._tree, "Raw participant data", KIND_RAW
        )
        self._item_raw.setDisabled(self._project.pdata is None)

        self._item_mapped = self._make_item(
            self._tree, "Mapped participant data", KIND_MAPPED
        )
        self._item_mapped.setDisabled(self._project.pdata is None)

        self._item_terms = self._make_item(
            self._tree, "Terminology", KIND_TERMS
        )
        self._item_terms.setDisabled(self._project.pdata is None)

        self._item_all = self._make_item(self._tree, "All", KIND_ALL)
        self._item_all.setDisabled(not self._project.setups)

        for setup in self._project.setups:
            setup_item = self._make_item(
                self._item_all, setup.name, KIND_SETUP, setup.setup_id
            )
            self._setup_items[setup.setup_id] = setup_item
            for a_id, a_name in zip(
                setup.allocation_ids, setup.allocation_names
            ):
                alloc_item = self._make_item(
                    setup_item, a_name, KIND_ALLOCATION, a_id
                )
                self._allocation_items[a_id] = alloc_item

        self._tree.expandAll()

    def _make_item(self, parent, text, kind, item_id=None) -> QTreeWidgetItem:
        item = QTreeWidgetItem(parent, [text])
        item.setData(0, _ROLE_KIND, kind)
        item.setData(0, _ROLE_ID, item_id)
        # Qt's ItemIsAutoTristate parent aggregation only works reliably
        # for items that have had an explicit checkstate set at least once
        # -- an item that's never had setCheckState() called is invisible
        # to it, silently breaking the parent's tristate computation.
        item.setCheckState(0, Qt.CheckState.Unchecked)
        return item

    # -- flat list of every tree item, for whole-tree operations ----------

    def _all_items(self) -> list[QTreeWidgetItem]:
        items = []

        def walk(item):
            items.append(item)
            for i in range(item.childCount()):
                walk(item.child(i))

        for i in range(self._tree.topLevelItemCount()):
            walk(self._tree.topLevelItem(i))
        return items

    # -- mode switching (XLSX checkboxes <-> CSV single selection) --------

    def _format_changed(self):
        is_csv = self._radio_csv.isChecked()
        self._set_mode(is_csv)
        self._apply_default_selection(is_csv)

    def _set_mode(self, is_csv: bool):
        self._csv_group.setEnabled(is_csv)
        self._tree.blockSignals(True)
        for item in self._all_items():
            kind = item.data(0, _ROLE_KIND)

            if kind == KIND_ALL:
                # QTreeWidgetItem.setDisabled() cascades ItemIsEnabled
                # removal down to *all* descendants, so it's only used
                # here when "All" truly has no children to protect (no
                # setups at all). In CSV mode with setups present, "All"
                # instead just loses selectability -- it can never
                # collapse into one CSV table, but its Setup/Allocation
                # children still can, and must stay enabled.
                if not self._project.setups:
                    item.setFlags(Qt.ItemFlag.NoItemFlags)
                    item.setDisabled(True)
                    item.setData(0, Qt.ItemDataRole.CheckStateRole, None)
                elif is_csv:
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    item.setData(0, Qt.ItemDataRole.CheckStateRole, None)
                else:
                    item.setFlags(
                        Qt.ItemFlag.ItemIsEnabled
                        | Qt.ItemFlag.ItemIsSelectable
                        | Qt.ItemFlag.ItemIsUserCheckable
                        | Qt.ItemFlag.ItemIsAutoTristate
                    )
                    item.setCheckState(0, Qt.CheckState.Unchecked)
                continue

            disabled = item.isDisabled()
            if is_csv:
                flags = (
                    Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
                )
                # CSV only ever allows a single component, so tick boxes
                # would be actively misleading here -- clear the check
                # state data entirely (not just the checkable flag), since
                # Qt's delegate still draws the indicator from that data
                # regardless of ItemIsUserCheckable.
                item.setData(0, Qt.ItemDataRole.CheckStateRole, None)
            else:
                flags = (
                    Qt.ItemFlag.ItemIsEnabled
                    | Qt.ItemFlag.ItemIsSelectable
                    | Qt.ItemFlag.ItemIsUserCheckable
                    | Qt.ItemFlag.ItemIsAutoTristate
                )
            item.setFlags(flags)
            item.setDisabled(disabled)
            if not is_csv:
                item.setCheckState(0, Qt.CheckState.Unchecked)
        self._tree.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
            if is_csv
            else QAbstractItemView.SelectionMode.NoSelection
        )
        self._tree.blockSignals(False)

    # -- cascading checkbox behaviour (XLSX mode only) ---------------------

    def _item_changed(self, item: QTreeWidgetItem, column: int):
        if self._updating or self._radio_csv.isChecked():
            return
        state = item.checkState(0)
        if state == Qt.CheckState.PartiallyChecked:
            return
        self._updating = True
        try:
            self._set_descendants_checked(item, state)
        finally:
            self._updating = False
        self._update_ok_enabled()

    def _set_descendants_checked(
        self, item: QTreeWidgetItem, state: Qt.CheckState
    ):
        for i in range(item.childCount()):
            child = item.child(i)
            if not child.isDisabled():
                child.setCheckState(0, state)
            self._set_descendants_checked(child, state)

    # -- default/initial selection ------------------------------------------

    def _apply_default_selection(self, is_csv: bool):
        self._updating = True
        try:
            if is_csv:
                self._tree.clearSelection()
                if self._project.setups and self._project.setups[0].ensemble:
                    first_setup = self._project.setups[0]
                    first_alloc_id = first_setup.allocation_ids[0]
                    self._tree.setCurrentItem(
                        self._allocation_items[first_alloc_id]
                    )
            else:
                for item in self._all_items():
                    if not item.isDisabled():
                        item.setCheckState(0, Qt.CheckState.Checked)
        finally:
            self._updating = False
        self._update_ok_enabled()

    def _apply_selection(self, selection: GSExportSelection, is_csv: bool):
        self._updating = True
        try:
            if is_csv:
                item = self._csv_item_for_selection(selection)
                if item is not None:
                    self._tree.setCurrentItem(item)
            else:
                self._item_raw.setCheckState(
                    0,
                    Qt.CheckState.Checked
                    if selection.raw_data
                    else Qt.CheckState.Unchecked,
                )
                self._item_mapped.setCheckState(
                    0,
                    Qt.CheckState.Checked
                    if selection.mapped_data
                    else Qt.CheckState.Unchecked,
                )
                self._item_terms.setCheckState(
                    0,
                    Qt.CheckState.Checked
                    if selection.terminology
                    else Qt.CheckState.Unchecked,
                )
                if selection.all_results:
                    self._item_all.setCheckState(0, Qt.CheckState.Checked)
                    self._set_descendants_checked(
                        self._item_all, Qt.CheckState.Checked
                    )
                else:
                    for setup in self._project.setups:
                        scope = selection.setups.get(setup.setup_id)
                        setup_item = self._setup_items[setup.setup_id]
                        if scope in ("all", "summary_only"):
                            setup_item.setCheckState(0, Qt.CheckState.Checked)
                            self._set_descendants_checked(
                                setup_item, Qt.CheckState.Checked
                            )
                        elif isinstance(scope, set):
                            for a_id in scope:
                                if a_id in self._allocation_items:
                                    self._allocation_items[a_id].setCheckState(
                                        0, Qt.CheckState.Checked
                                    )
        finally:
            self._updating = False
        self._update_ok_enabled()

    def _csv_item_for_selection(
        self, selection: GSExportSelection
    ) -> None | QTreeWidgetItem:
        if selection.raw_data:
            return self._item_raw
        if selection.mapped_data:
            return self._item_mapped
        if selection.terminology:
            return self._item_terms
        for setup_id, scope in selection.setups.items():
            if scope == "summary_only" and setup_id in self._setup_items:
                return self._setup_items[setup_id]
            if isinstance(scope, set):
                for a_id in scope:
                    if a_id in self._allocation_items:
                        return self._allocation_items[a_id]
        return None

    # -- OK button enablement -------------------------------------------------

    def _update_ok_enabled(self):
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            not self.get_selection().is_empty()
        )

    # -- reading back the dialog's result -----------------------------------

    def get_format(self) -> str:
        """Return "xlsx" or "csv", whichever format is currently chosen."""
        return "xlsx" if self._radio_xlsx.isChecked() else "csv"

    def get_csv_options(self) -> tuple[str, str]:
        """Return the chosen (separator, quote character) for CSV."""
        return self._csv_sep.currentData(), self._csv_quote.currentData()

    def get_selection(self) -> GSExportSelection:
        """Return the currently chosen component selection."""
        if self._radio_csv.isChecked():
            return self._selection_from_csv_item(self._tree.currentItem())

        selection = GSExportSelection(
            raw_data=self._item_raw.checkState(0) == Qt.CheckState.Checked,
            mapped_data=self._item_mapped.checkState(0)
            == Qt.CheckState.Checked,
            terminology=self._item_terms.checkState(0)
            == Qt.CheckState.Checked,
            all_results=self._item_all.checkState(0) == Qt.CheckState.Checked,
        )
        if not selection.all_results:
            for setup in self._project.setups:
                setup_item = self._setup_items[setup.setup_id]
                state = setup_item.checkState(0)
                if state == Qt.CheckState.Checked:
                    selection.setups[setup.setup_id] = "all"
                elif state == Qt.CheckState.PartiallyChecked:
                    checked_ids = {
                        a_id
                        for a_id in setup.allocation_ids
                        if self._allocation_items[a_id].checkState(0)
                        == Qt.CheckState.Checked
                    }
                    if checked_ids:
                        selection.setups[setup.setup_id] = checked_ids
        return selection

    def _selection_from_csv_item(
        self, item: None | QTreeWidgetItem
    ) -> GSExportSelection:
        selection = GSExportSelection()
        if item is None:
            return selection
        kind = item.data(0, _ROLE_KIND)
        item_id = item.data(0, _ROLE_ID)
        if kind == KIND_RAW:
            selection.raw_data = True
        elif kind == KIND_MAPPED:
            selection.mapped_data = True
        elif kind == KIND_TERMS:
            selection.terminology = True
        elif kind == KIND_SETUP:
            selection.setups[item_id] = "summary_only"
        elif kind == KIND_ALLOCATION:
            setup_id = item.parent().data(0, _ROLE_ID)
            selection.setups[setup_id] = {item_id}
        return selection

    @classmethod
    def get_input(
        cls,
        parent: QWidget,
        project: GSProject,
        initial_settings: None | GSExportSettings = None,
    ) -> tuple[
        bool, None | str, None | str, None | str, None | GSExportSelection
    ]:
        """Show the dialog; return (ok, format, sep, quote, selection)."""
        dialog = cls(
            parent,
            project,
            initial_format=(
                initial_settings.file_format if initial_settings else "xlsx"
            ),
            initial_csv_sep=(
                initial_settings.csv_sep if initial_settings else ";"
            ),
            initial_csv_quote=(
                initial_settings.csv_quote if initial_settings else '"'
            ),
            initial_selection=(
                initial_settings.selection if initial_settings else None
            ),
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False, None, None, None, None
        csv_sep, csv_quote = dialog.get_csv_options()
        return (
            True,
            dialog.get_format(),
            csv_sep,
            csv_quote,
            dialog.get_selection(),
        )
