"""The Results tab: a tree of setups/allocations and a view of the selected."""

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QWidget,
    QTreeView,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QStackedWidget,
    QMenu,
    QInputDialog,
    QMessageBox,
)

from results.GSResultTableView import GSResultTableView
from results.GSSetupSummaryTableView import GSSetupSummaryTableView

if TYPE_CHECKING:
    from base_app.AppContext import AppContext


class GSResultsTab(QWidget):
    """Tab with a tree of setups/allocations and a view of the selected one."""

    _ctx: "AppContext"

    def __init__(self, ctx: "AppContext"):
        """Initialise the tab and build the results tree and views."""
        super(GSResultsTab, self).__init__()
        self._ctx = ctx

        self._create_ui()

    def _create_ui(self):
        # Tree of setups (ensembles) and their allocations (rounds).
        self._tree = QTreeView(parent=self)
        self._tree.setModel(self._ctx.model_manager["results_tree"])
        self._tree.setHeaderHidden(True)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._tree_context_menu)
        self._tree.selectionModel().currentChanged.connect(
            self._selection_changed
        )

        self._btn_rename = QPushButton("Rename")
        self._btn_rename.clicked.connect(self._rename_current)
        self._btn_delete = QPushButton("Delete")
        self._btn_delete.clicked.connect(self._delete_current)

        tree_layout = QVBoxLayout()
        tree_layout.addWidget(self._tree)
        tree_layout.addWidget(self._btn_rename)
        tree_layout.addWidget(self._btn_delete)
        tree_widget = QWidget()
        tree_widget.setLayout(tree_layout)

        # Table showing one single allocation.
        self._results_table = GSResultTableView(parent=self)
        self._results_table.setModel(self._ctx.model_manager["results_table"])

        # Table showing the summary across one setup's allocations.
        self._summary_table = GSSetupSummaryTableView(parent=self)
        self._summary_table.setModel(
            self._ctx.model_manager["results_summary"]
        )

        self._stack = QStackedWidget(parent=self)
        self._stack.addWidget(self._results_table)
        self._stack.addWidget(self._summary_table)

        layout = QGridLayout()
        layout.addWidget(tree_widget, 0, 0)
        layout.addWidget(self._stack, 0, 1)
        layout.setColumnStretch(1, 10)
        self.setLayout(layout)

    def refresh_selection(self):
        """Sync the tree's selection and visible table to the project."""
        project = self._ctx.project_manager.project
        if (
            project is None
            or project.selected_setup is None
            or project.selected_setup >= len(project.setups)
        ):
            self._tree.setCurrentIndex(QModelIndex())
            return

        model = self._ctx.model_manager["results_tree"]
        if project.selected_allocation is None:
            index = model.index_for_setup(project.selected_setup)
        else:
            setup = project.setups[project.selected_setup]
            if project.selected_allocation >= len(setup.ensemble):
                self._tree.setCurrentIndex(QModelIndex())
                return
            index = model.index_for_allocation(
                project.selected_setup, project.selected_allocation
            )

        self._tree.expand(model.index_for_setup(project.selected_setup))
        self._tree.setCurrentIndex(index)
        # setCurrentIndex() only emits currentChanged() when the index
        # actually moves, so make sure the visible table matches even when
        # it was already selected (e.g. re-generating into the same setup).
        self._selection_changed(index, index)

    def _selection_changed(self, current: QModelIndex, previous: QModelIndex):
        if not current.isValid():
            return
        model = self._ctx.model_manager["results_tree"]
        setup_row, allocation_row = model.node(current)
        if allocation_row is None:
            self._ctx.model_manager["results_summary"].update_current(
                setup_row
            )
            self._stack.setCurrentWidget(self._summary_table)
        else:
            self._ctx.model_manager["results_table"].update_current(
                setup_row, allocation_row
            )
            self._stack.setCurrentWidget(self._results_table)

    def _tree_context_menu(self, pos):
        index = self._tree.indexAt(pos)
        if not index.isValid():
            return
        self._tree.setCurrentIndex(index)

        menu = QMenu()
        action_rename = QAction("Rename", self)
        menu.addAction(action_rename)
        action_delete = QAction("Delete", self)
        menu.addAction(action_delete)

        action_clicked = menu.exec_(self._tree.viewport().mapToGlobal(pos))
        if action_clicked == action_rename:
            self._rename_current()
        elif action_clicked == action_delete:
            self._delete_current()

    def _current_node(self):
        """Return (setup, setup_row, allocation_row) for the current index."""
        index = self._tree.currentIndex()
        if not index.isValid():
            return None
        model = self._ctx.model_manager["results_tree"]
        project = self._ctx.project_manager.project
        setup_row, allocation_row = model.node(index)
        if setup_row >= len(project.setups):
            return None
        return project.setups[setup_row], setup_row, allocation_row

    def _rename_current(self):
        node = self._current_node()
        if node is None:
            return
        setup, setup_row, allocation_row = node

        old_name = (
            setup.name
            if allocation_row is None
            else setup.allocation_names[allocation_row]
        )
        new_name, ok = QInputDialog.getText(
            self._ctx.main_window,
            "Rename",
            "Name:",
            text=old_name,
        )
        if not ok or not new_name:
            return

        if allocation_row is None:
            setup.name = new_name
        else:
            setup.allocation_names[allocation_row] = new_name
        self._ctx.model_manager.updated_results()
        self._ctx.set_unsaved()

    def _delete_current(self):
        node = self._current_node()
        if node is None:
            return
        setup, setup_row, allocation_row = node
        project = self._ctx.project_manager.project

        if allocation_row is None:
            question = f'Delete setup "{setup.name}" and all its rounds?'
        else:
            allocation_name = setup.allocation_names[allocation_row]
            question = f'Delete round "{allocation_name}"?'
        reply = QMessageBox.question(
            self._ctx.main_window,
            "Confirm delete",
            question,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        if allocation_row is None:
            del project.setups[setup_row]
        else:
            del setup.ensemble[allocation_row]
            del setup.allocation_names[allocation_row]

        # Clear the current selection, since whatever was selected may no
        # longer exist.
        project.selected_setup = None
        project.selected_allocation = None
        self._tree.setCurrentIndex(QModelIndex())

        self._ctx.model_manager.updated_results()
        self._ctx.set_unsaved()
