from pathlib import Path

from base_app.AbstractMainWindow import AbstractMainWindow
from datahandling import FILE_TYPE_CSV, FILE_TYPE_XLS
from GSMainTabs import GSMainTabs
from importing.GSDataImportHandle import GSDataImportHandle
from importing.GSPreviewDialog import GSPreviewDialog
from PySide6.QtWidgets import QFileDialog, QMessageBox


class GSMainWindow(AbstractMainWindow):
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
                        "desc": "Import people data from file saved on "
                        "current device.",
                        "show_when_closed": False,
                        "trigger": self._import_file,
                    },
                    "update": {
                        "type": "action",
                        "name": "&Update import",
                        "shortcut": "Shift+F5",
                        "desc": "Update imported data from previously "
                        "imported source.",
                        "show_when_closed": False,
                        "trigger": self._import_update,
                    },
                },
            },
            "help": _super_menu["help"],
        }

    def _create_main_widget(self) -> GSMainTabs:
        return GSMainTabs(self._ctx, self)

    def update_project_status(self):
        super(GSMainWindow, self).update_project_status()
        if self._ctx.is_open:
            self._main_widget.project_opened()

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
                    + str(file_path.absolute()),
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
                        "File type could not be determined from file ending:"
                        + str(file_path.absolute()),
                    )
                    return

            # Create DataHandle object from file path and file type.
            data_handle = GSDataImportHandle(
                file_path=file_path,
                file_type=file_type,
            )

            # Open dialog to preview data and select columns for importing.
            ok = GSPreviewDialog.display(
                parent=self._ctx.main_window,
                data_handle=data_handle,
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
