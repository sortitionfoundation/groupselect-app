"""The main application window, adding the app-specific Data menu."""

from pathlib import Path

from PySide6 import QtCore
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
    QProgressDialog,
)

from datahandling import FILE_TYPE_XLS, FILE_TYPE_CSV
from base_app.AbstractMainWindow import AbstractMainWindow

from GSExportSettings import GSExportSettings
from GSMainTabs import GSMainTabs
from exporting.GSExportContent import export_to_file
from exporting.GSExportDialog import GSExportDialog
from importing.DataImportHandle import DataImportHandle
from importing.GSPreviewDialog import GSPreviewDialog


class GSMainWindow(AbstractMainWindow):
    """The application's main window."""

    def _define_menu(self) -> dict[str, dict]:
        _super_menu = super(GSMainWindow, self)._define_menu()
        return {
            "project": _super_menu["project"],
            "data": {
                "name": "Data",
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
