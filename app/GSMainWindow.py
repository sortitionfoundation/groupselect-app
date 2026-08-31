"""The main application window, adding the app-specific menus."""

from pathlib import Path

import pandas as pd
from PySide6 import QtCore
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMenu,
    QMessageBox,
    QProgressDialog,
)

from datahandling import FILE_TYPE_XLS, FILE_TYPE_CSV
from groupselect.examples import DATA_DIR
from base_app.AbstractMainWindow import AbstractMainWindow

from GSExportSettings import GSExportSettings
from GSMainTabs import GSMainTabs
from exampledata.ExampleDataHandle import (
    ExampleDataHandle,
    PredefinedExampleDataHandle,
    SyntheticExampleDataHandle,
)
from exporting.GSExportContent import export_to_file
from exporting.GSExportDialog import GSExportDialog
from importing.DataImportHandle import DataImportHandle
from importing.GSPreviewDialog import GSPreviewDialog


# Participant counts offered in the "Synthetic dataset" submenu.
SYNTHETIC_DATASET_SIZES = [20, 40, 60, 80, 100]


class GSMainWindow(AbstractMainWindow):
    """The application's main window."""

    def _define_menu(self) -> dict[str, dict]:
        _super_menu = super(GSMainWindow, self)._define_menu()
        return {
            "project": _super_menu["project"],
            "data": {
                "name": "&Data",
                "items": {
                    "load": {
                        "type": "action",
                        "name": "&Import file",
                        "shortcut": "Ctrl+I",
                        "desc": (
                            "Import people data from file saved on "
                            "current device."
                        ),
                        "show_when_closed": False,
                        "trigger": self._import_file,
                    },
                    "update": {
                        "type": "action",
                        "name": "&Update import",
                        "shortcut": "Shift+F5",
                        "desc": (
                            "Update imported data from previously "
                            "imported source."
                        ),
                        "show_when_closed": False,
                        "trigger": self._import_update,
                    },
                    "sep1": {
                        "type": "separator",
                    },
                    "export_as": {
                        "type": "action",
                        "name": "&Export as...",
                        "shortcut": "Ctrl+E",
                        "desc": (
                            "Choose what to export and where, then export "
                            "participants' data and/or results to a file."
                        ),
                        "show_when_closed": False,
                        "trigger": self._export_as,
                    },
                    "export": {
                        "type": "action",
                        "name": "Export",
                        "shortcut": "Ctrl+Shift+E",
                        "desc": "Repeat the last successful export.",
                        "show_when_closed": False,
                        "trigger": self._export_repeat,
                    },
                },
            },
            "help": _super_menu["help"],
        }

    def _create_menu(self):
        super(GSMainWindow, self)._create_menu()
        self._create_load_example_menu()
        self._apply_menu_tooltips()

    def _apply_menu_tooltips(self):
        """Surface each action's status-bar description as a tooltip too.

        `base_app` only wires a menu item's `'desc'` up to
        `QAction.setStatusTip()`, but this app never calls `statusBar()`,
        so that description would otherwise never actually be shown to the
        user -- mirror it onto `setToolTip()` for every menu (this repo's
        "Data" menu included) so hovering the item shows it instead.
        """
        for menu in self._menus.values():
            menu.setToolTipsVisible(True)
        for menu_id, menu_specs in self._define_menu().items():
            for item_id, item_specs in menu_specs["items"].items():
                if item_specs["type"] == "action" and "desc" in item_specs:
                    self._menu_items[f"{menu_id}:{item_id}"].setToolTip(
                        item_specs["desc"]
                    )

    def _create_load_example_menu(self):
        """Insert the hierarchical "Load example" submenu into "Data".

        `base_app`'s menu system only knows flat actions/separators (see
        `AbstractMainWindow._create_menu`), so this submenu tree is built
        directly with Qt and spliced into the already-built "Data" menu,
        as its own section below "Import file"/"Update import" and above
        "Export as..."/"Export".
        """
        data_menu = self._menus["data"]
        export_as_action = self._menu_items["data:export_as"]

        menu = QMenu("Load &example", self)
        menu.setToolTipsVisible(True)
        menu.menuAction().setToolTip(
            "Load a ready-made or synthetically generated example "
            "dataset, useful for trying out the app without your own data."
        )
        data_menu.insertMenu(export_as_action, menu)
        data_menu.insertSeparator(export_as_action)

        action = menu.addAction("&Default example")
        desc = "Load the default example dataset bundled with groupselect."
        action.setStatusTip(desc)
        action.setToolTip(desc)
        action.triggered.connect(self._load_example_default)

        menu.addSeparator()

        predefined_menu = menu.addMenu("&Predefined datasets")
        predefined_menu.setToolTipsVisible(True)
        for csv_path in sorted(DATA_DIR.glob("*.csv")):
            if csv_path.stem == "default":
                continue
            n_participants = len(pd.read_csv(csv_path))
            action = predefined_menu.addAction(
                f"{csv_path.stem} ({n_participants} participants)"
            )
            action.setToolTip(
                f"Load the '{csv_path.stem}' example dataset, with "
                f"{n_participants} participants."
            )
            action.triggered.connect(
                lambda checked=False, path=csv_path: (
                    self._load_example_predefined(path)
                )
            )

        synthetic_menu = menu.addMenu("&Synthetic dataset")
        synthetic_menu.setToolTipsVisible(True)
        for n_participants in SYNTHETIC_DATASET_SIZES:
            action = synthetic_menu.addAction(f"{n_participants} participants")
            action.setToolTip(
                f"Generate a random synthetic example dataset with "
                f"{n_participants} participants."
            )
            action.triggered.connect(
                lambda checked=False, n=n_participants: (
                    self._load_example_synthetic(n)
                )
            )

    def _create_main_widget(self) -> GSMainTabs:
        return GSMainTabs(self._ctx, self)

    def update_project_status(self):
        """Update the UI to reflect whether a project is currently open."""
        super(GSMainWindow, self).update_project_status()
        if self._ctx.is_open:
            self._main_widget.project_opened()
        self._update_export_enabled()

    def _update_export_enabled(self):
        """Enable "Export" only once a first "Export as..." has succeeded."""
        project = self._ctx.project_manager.project
        can_repeat = (
            self._ctx.is_open
            and project is not None
            and project.export_settings is not None
        )
        self._menu_items["data:export"].setEnabled(can_repeat)

    def _import_file(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self._ctx.main_window,
                "Import file",
                None,
                "Excel spreadsheets (*.xls, *.xlsx);;Delimiter-separated "
                "plain-text files (*.csv, *.tsv, *.ssv)",
            )
            if not file_path:
                return
            file_path = Path(file_path)

            if not (file_path.exists() and file_path.is_file()):
                QMessageBox.critical(
                    self._ctx.main_window,
                    "File not found",
                    "File does not exist or could not be opened:\n\n"
                    f"{file_path.absolute()}",
                )
                return

            # Determined file type from file name suffix.
            match file_path.suffix:
                case ".xls" | ".xlsx":
                    file_type = FILE_TYPE_XLS
                case ".csv" | ".tsv" | ".ssv":
                    file_type = FILE_TYPE_CSV
                case _:
                    QMessageBox.critical(
                        self._ctx.main_window,
                        "Unknown file type",
                        "File type could not be determined from file "
                        f"ending:\n\n{file_path.absolute()}",
                    )
                    return

            # Create DataHandle object from file path and file type.
            data_handle = DataImportHandle(
                file_path=file_path, file_type=file_type
            )

            # Open dialog to preview data and select columns for importing.
            ok = GSPreviewDialog.display(
                parent=self._ctx.main_window, data_handle=data_handle
            )
            if not ok:
                return

            # Import data and store inside data_handle
            data_handle.import_data()
        except Exception as ex:
            QMessageBox.critical(
                self._ctx.main_window,
                "Error",
                f"Unknown error occurred:\n\n{ex}",
            )
        else:
            # Add DataHandle to project.
            self._ctx.project_manager.project.data_handle = data_handle

            # Update models and displays.
            self._ctx.model_manager.updated_participants()

    def _import_update(self):
        # Update imported data that is stored inside data_handle.
        try:
            self._ctx.project_manager.project.data_handle.import_data()
        except Exception as ex:
            QMessageBox.critical(
                self._ctx.main_window,
                "Error",
                f"Unknown error occurred:\n\n{ex}",
            )

        # Update models and displays.
        self._ctx.model_manager.updated_participants()

    def _load_example_default(self):
        self._load_example(
            lambda: PredefinedExampleDataHandle(DATA_DIR / "default.csv")
        )

    def _load_example_predefined(self, csv_path: Path):
        self._load_example(lambda: PredefinedExampleDataHandle(csv_path))

    def _load_example_synthetic(self, n_participants: int):
        self._load_example(lambda: SyntheticExampleDataHandle(n_participants))

    def _load_example(self, make_data_handle):
        """Build an example data handle and load it into the project.

        The data is generated/read already ready to use, so -- unlike a
        real import -- there is no preview dialogue to go through first.
        """
        try:
            data_handle: ExampleDataHandle = make_data_handle()
        except Exception as ex:
            QMessageBox.critical(
                self._ctx.main_window,
                "Error",
                f"Unknown error occurred:\n\n{ex}",
            )
            return

        # Add DataHandle to project.
        self._ctx.project_manager.project.data_handle = data_handle

        # Update models and displays.
        self._ctx.model_manager.updated_participants()

    def _export_as(self):
        project = self._ctx.project_manager.project

        ok, file_format, csv_sep, csv_quote, selection = (
            GSExportDialog.get_input(
                self._ctx.main_window, project, project.export_settings
            )
        )
        if not ok:
            return

        if file_format == "xlsx":
            caption = "Export as Excel workbook"
            file_filter = "Excel workbook (*.xlsx)"
            suffix = ".xlsx"
        else:
            caption = "Export as CSV"
            file_filter = "CSV file (*.csv)"
            suffix = ".csv"

        file_path, _ = QFileDialog.getSaveFileName(
            self._ctx.main_window, caption, None, file_filter
        )
        if not file_path:
            return
        if not file_path.endswith(suffix):
            file_path += suffix

        settings = GSExportSettings(
            file_path,
            file_format,
            csv_sep=csv_sep,
            csv_quote=csv_quote,
            selection=selection,
        )
        if self._run_export(settings):
            # Remember this configuration so a plain "Export" can repeat
            # it later without re-prompting.
            project.export_settings = settings
            self._ctx.set_unsaved()
            self._update_export_enabled()

    def _export_repeat(self):
        project = self._ctx.project_manager.project
        if project.export_settings is None:
            return
        self._run_export(project.export_settings)

    def _run_export(self, settings: GSExportSettings) -> bool:
        """Write `settings` to disk behind a busy popup. Return success."""
        project = self._ctx.project_manager.project

        progress = QProgressDialog(
            "Exporting data...", "", 0, 0, self._ctx.main_window
        )
        progress.setWindowTitle("Exporting...")
        progress.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()

        try:
            export_to_file(project, settings)
        except Exception as ex:
            progress.close()
            QMessageBox.critical(
                self._ctx.main_window,
                "Error",
                f"An error occurred during export: {ex}",
            )
            return False
        else:
            progress.close()
            return True
