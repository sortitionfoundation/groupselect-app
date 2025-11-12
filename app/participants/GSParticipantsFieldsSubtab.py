from PySide6.QtWidgets import QWidget, QHeaderView, QHBoxLayout, QListView, QTableView

from base_app.AppContext import AppContext


class GSParticipantsFieldsSubtab(QWidget):
    def __init__(self, ctx: 'AppContext'):
        super(GSParticipantsFieldsSubtab, self).__init__()
        self._ctx = ctx

        self._create_ui()

    def _create_ui(self):
        self.fields_list = QListView()
        self.fields_list.setModel(self._ctx.model_manager['pfields'])
        self.fields_list.selectionModel().currentChanged.connect(self.fieldlist_select)

        self.terms_table = QTableView()
        self.terms_table.setModel(self._ctx.model_manager['pterms'])
        self.terms_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.terms_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.fields_list)
        layout.addWidget(self.terms_table)
        self.setLayout(layout)

        self.termslist_disable()

    def termslist_enable(self):
        self.terms_table.setDisabled(False)

    def termslist_disable(self):
        self.terms_table.setDisabled(True)

    def fieldlist_select(self, current):
        self.termslist_enable()
        self._ctx.model_manager['pterms'].update_key(current.row())

    def clear(self):
        self.fields_list.clearSelection()
        self._ctx.model_manager['pterms'].update_key(None)
