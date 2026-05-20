import copy

import pandas as pd
from datahandling import (
    FILE_QUOTE_OPTIONS,
    FILE_SEP_OPTIONS,
    FILE_TYPE_CSV,
    FILE_TYPE_XLS,
)
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .GSDataImportHandle import GSDataImportHandle
from .GSPreviewTableModel import GSPreviewTableModel
from .GSPreviewTableView import GSPreviewTableView


class GSPreviewDialog(QDialog):
    _data_handle: GSDataImportHandle
    _ok: bool = False
    _data: None | pd.DataFrame = None
    _file_config: dict = {}
    _column_naming: dict = {}

    def __init__(self, parent: QWidget, data_handle: GSDataImportHandle):
        # Super constructor.
        super(GSPreviewDialog, self).__init__(parent=parent)

        # Store arguments.
        self._data_handle: GSDataImportHandle = data_handle

        # Read data from data file.
        self._read_data()

        # Initialise config and mapping from data file.
        self._init()

        # Add models.
        self._table_model = GSPreviewTableModel(self)

        # Create UI.
        self._create_ui()

    @property
    def data(self) -> pd.DataFrame:
        return self._data

    @property
    def file_config(self) -> dict:
        return self._file_config

    @property
    def column_naming(self) -> dict[int, str]:
        return self._column_naming

    @column_naming.setter
    def column_naming(self, column_naming: dict[int, str]):
        self._column_naming = column_naming

    def _read_data(self):
        self._data = self._data_handle.preview(file_config=self._file_config)

    def _init(self):
        # Load dialog config once from data_file object.
        self._file_config = copy.deepcopy(self._data_handle.file_config)
        self._column_naming = {
            k: (
                self._data_handle.column_naming[k]
                if k in self._data_handle.column_naming
                else None
            )
            for k in range(len(self._data.columns))
        }

        if self._file_config["first"] is None:
            self._file_config["first"] = 2
        if self._file_config["last"] is None or self._file_config[
            "last"
        ] > len(self._data):
            self._file_config["last"] = len(self._data)

    def _create_ui(self):
        # Add first and last spin boxes.
        buttons_layout = QHBoxLayout()
        self._field_first = QSpinBox()
        self._field_first.setRange(1, len(self._data))
        self._field_first.setSingleStep(1)
        self._field_first.setValue(self._file_config["first"])
        self._field_first.valueChanged.connect(self._update_first_final)
        buttons_layout.addWidget(self._field_first)
        self._field_last = QSpinBox()
        self._field_last.setRange(1, len(self._data))
        self._field_last.setSingleStep(1)
        self._field_last.setValue(self._file_config["last"])
        self._field_last.valueChanged.connect(self._update_first_final)
        buttons_layout.addWidget(self._field_last)

        # Add XLS and CSV specific fields.
        if self._data_handle.file_type == FILE_TYPE_XLS:
            field_sheet = QComboBox()
            field_sheet.addItems(
                pd.ExcelFile(self._data_handle.file_path).sheet_names
            )
            field_sheet.setCurrentIndex(
                self._data_handle.file_config["sheet_name"]
            )
            field_sheet.currentIndexChanged.connect(self._update_sheet)
            buttons_layout.addWidget(field_sheet)
        elif self._data_handle.file_type == FILE_TYPE_CSV:
            field_sep = QComboBox()
            field_sep.addItems(list(FILE_SEP_OPTIONS.values()))
            field_sep.setCurrentIndex(
                list(FILE_SEP_OPTIONS.keys()).index(
                    self._data_handle.file_config["sep"]
                )
            )
            field_sep.currentIndexChanged.connect(self._update_sep)
            buttons_layout.addWidget(field_sep)
            field_quote = QComboBox()
            field_quote.addItems(list(FILE_QUOTE_OPTIONS.values()))
            field_quote.setCurrentIndex(
                list(FILE_QUOTE_OPTIONS.keys()).index(
                    self._data_handle.file_config["quotechar"]
                )
            )
            field_quote.currentIndexChanged.connect(self._update_quote)
            buttons_layout.addWidget(field_quote)

        fields = QWidget()
        fields.setLayout(buttons_layout)

        # Set main table widget.
        table = GSPreviewTableView(self._table_model, self)

        # Set dialog buttons.
        self._btn_auto = QPushButton("&Auto-detect headings")
        self._btn_auto.clicked.connect(self._button_clicked)
        self._btn_ok = QPushButton("&Ok")
        self._btn_ok.clicked.connect(self._button_clicked)
        self._btn_cancel = QPushButton("&Cancel")
        self._btn_cancel.clicked.connect(self._button_clicked)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self._btn_auto)
        buttons_layout.addWidget(self._btn_ok)
        buttons_layout.addWidget(self._btn_cancel)
        buttons = QWidget()
        buttons.setLayout(buttons_layout)

        # Set dialog layout.
        layout = QVBoxLayout()
        layout.addWidget(fields)
        layout.addWidget(table)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _button_clicked(self):
        sender = self.sender()
        if sender == self._btn_auto:
            self._table_model.auto_detect_column_names(
                self._file_config["first"] - 1
            )
        elif sender == self._btn_ok:
            self._ok = True
            self.close()
        elif sender == self._btn_cancel:
            self.close()
        else:
            raise Exception("Unknown button pressed.")

    def _update_first_final(self):
        self._file_config |= {
            "first": self._field_first.value(),
            "last": self._field_last.value(),
        }
        self._table_model.layoutChanged.emit()

    def _update_sheet(self, index: int):
        if index == self._file_config["sheet_name"]:
            return
        self._file_config["sheet_name"] = index
        self._read_data()
        self._table_model.layoutChanged.emit()

    def _update_sep(self, index: int):
        self._file_config["sep"] = list(FILE_SEP_OPTIONS.keys())[index]
        self._read_data()
        self._table_model.layoutChanged.emit()

    def _update_quote(self, index: int):
        self._file_config["quotechar"] = list(FILE_QUOTE_OPTIONS.keys())[index]
        self._read_data()
        self._table_model.layoutChanged.emit()

    @classmethod
    def display(cls, parent: QWidget, data_handle: GSDataImportHandle):
        dialog = cls(parent, data_handle=data_handle)
        dialog.showMaximized()
        dialog.setWindowTitle(f"Importing from {data_handle.title}")
        dialog.exec_()
        if dialog._ok:
            data_handle.update_file_config(**dialog._file_config)
            data_handle.update_column_naming(dialog._column_naming)
        return dialog._ok
