from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QLineEdit, \
                            QListWidget, QGroupBox, QGridLayout, QFormLayout, QListWidgetItem, QProgressDialog
from PyQt5.QtGui import QIntValidator

from org.sortition.groupselect.gui.maintabs.generate.TAManualDialog import TAManualDialog
from org.sortition.groupselect.gui.maintabs.generate.TAListMove import TAListMove
from org.sortition.groupselect.gui.maintabs.generate.TAAdvancedSettingsDialog import TAAdvancedSettingsDialog

class TAGenerateTab(QWidget):
    def __init__(self, ctx):
        super(TAGenerateTab, self).__init__()
        self.ctx = ctx

        self._table_being_updated = False
        self._order_lists_being_updated = False
        self._settings_being_updated = False

        self.create_ui()

    def create_ui(self):
        settings_layout = QHBoxLayout()

        self.order_cluster = TAListMove()
        self.order_cluster.trigger.connect(self.userchanged_order_lists)
        order_cluster_layout = QVBoxLayout()
        order_cluster_layout.addWidget(self.order_cluster)
        order_cluster_group = QGroupBox("Cluster Order")
        order_cluster_group.setLayout(order_cluster_layout)

        self.order_diverse = TAListMove()
        self.order_diverse.trigger.connect(self.userchanged_order_lists)
        order_diverse_layout = QVBoxLayout()
        order_diverse_layout.addWidget(self.order_diverse)
        order_diverse_group = QGroupBox("Diversify Order")
        order_diverse_group.setLayout(order_diverse_layout)

        self.order_manual = QListWidget()
        btn1 = QPushButton("Create")
        btn1.clicked.connect(self.buttonclicked_manual_add)
        btn2 = QPushButton("Delete")
        btn2.clicked.connect(self.buttonclicked_manual_del)
        order_manual_btnlst = QHBoxLayout()
        order_manual_btnlst.addWidget(btn1)
        order_manual_btnlst.addWidget(btn2)
        order_manual_btnlst_widget = QWidget()
        order_manual_btnlst_widget.setLayout(order_manual_btnlst)
        order_manual_layout = QVBoxLayout()
        order_manual_layout.addWidget(self.order_manual)
        order_manual_layout.addWidget(order_manual_btnlst_widget)
        order_manual_group = QGroupBox("Manual Allocation")
        order_manual_group.setLayout(order_manual_layout)

        settings_layout.addWidget(order_cluster_group)
        settings_layout.addWidget(order_diverse_group)
        settings_layout.addWidget(order_manual_group)

        settings_group = QGroupBox("Field Settings")
        settings_group.setLayout(settings_layout)

        run_layout = QHBoxLayout()

        run_settings1_layout = QFormLayout()

        self.seats_field = QLineEdit()
        self.seats_field.setValidator( QIntValidator(1, 16, self) );
        self.seats_field.textChanged.connect(self.userchanged_settings_fields)

        self.tables_field = QLineEdit()
        self.tables_field.setValidator( QIntValidator(1, 100, self) );
        self.tables_field.textChanged.connect(self.userchanged_settings_fields)

        run_settings1_layout.addRow(QLabel("Num. of Groups"), self.tables_field)
        run_settings1_layout.addRow(QLabel("Num. of People per Group"), self.seats_field)

        run_settings1_layout_widget = QWidget()
        run_settings1_layout_widget.setLayout(run_settings1_layout)

        run_settings2_layout = QFormLayout()

        self.number_field = QLineEdit()
        self.number_field.setValidator( QIntValidator(1, 16, self) );
        self.number_field.textChanged.connect(self.userchanged_settings_fields)

        run_settings2_layout.addRow(QLabel("Number of Allocations"), self.number_field)
        run_advanced_settings_button = QPushButton("Change Settings")
        run_advanced_settings_button.clicked.connect(self.buttonclicked_advanced_settings)
        run_settings2_layout.addRow(QLabel("Advanced Settings"), run_advanced_settings_button)

        run_settings2_layout_widget = QWidget()
        run_settings2_layout_widget.setLayout(run_settings2_layout)

        run_settings3_layout = QGridLayout()

        run_button = QPushButton("Generate Groups!")
        run_button.clicked.connect(self.buttonclicked_run_allocation)

        run_settings3_layout_widget = QWidget()
        run_settings3_layout_widget.setLayout(run_settings3_layout)

        run_layout.addWidget(run_settings1_layout_widget, 1)
        run_layout.addWidget(run_settings2_layout_widget, 1)
        run_layout.addWidget(run_button, 1)

        run_group = QGroupBox("Allocation Settings")
        run_group.setLayout(run_layout)

        layout = QGridLayout()
        layout.addWidget(settings_group, 0, 0)
        layout.addWidget(run_group, 1, 0)
        layout.setRowStretch(0,1)
        self.setLayout(layout)

    def init_order_list(self):
        for j in self.ctx.app_data.order_cluster:
            if j not in self.ctx.__dataManager.get_fields_with_mode('cluster'):
                self.ctx.app_data.order_cluster.remove(j)

        for j in self.ctx.__dataManager.get_fields_with_mode('cluster'):
            if j not in self.ctx.app_data.order_cluster:
                self.ctx.app_data.order_cluster.append(j)

        for j in self.ctx.app_data.order_diverse:
            if j not in self.ctx.__dataManager.get_fields_with_mode('diversify'):
                self.ctx.app_data.order_diverse.remove(j)

        for j in self.ctx.__dataManager.get_fields_with_mode('diversify'):
            if j not in self.ctx.app_data.order_diverse:
                self.ctx.app_data.order_diverse.append(j)

    def update_field_order_lists(self):
        self.init_order_list()

        self._order_lists_being_updated = True

        self.order_cluster.clear()
        for j in self.ctx.app_data.order_cluster:
            new_item = QListWidgetItem()
            new_item.setData(Qt.UserRole, j)
            new_item.setText(self.ctx.app_data.peopledata_keys[j])
            self.order_cluster.addItem(new_item)

        self.order_diverse.clear()
        for j in self.ctx.app_data.order_diverse:
            new_item = QListWidgetItem()
            new_item.setData(Qt.UserRole, j)
            new_item.setText(self.ctx.app_data.peopledata_keys[j])
            self.order_diverse.addItem(new_item)

        self._order_lists_being_updated = False

    def update_manuals_list(self):
        self.order_manual.clear()

        for m in self.ctx.app_data.manuals:
            self.order_manual.addItem("{0}: Table {1}".format(self.ctx.__dataManager.get_print_labels(m[0]), m[1] + 1))

    def update_settings(self):
        self._settings_being_updated = True

        self.tables_field.setText(str(self.ctx.app_data.settings['tables']))
        self.seats_field.setText(str(self.ctx.app_data.settings['seats']))

        self.number_field.setText(str(self.ctx.app_data.settings['nallocations']))

        self._settings_being_updated = False

    def userchanged_order_lists(self):
        if self._order_lists_being_updated: return

        self.ctx.app_data.order_cluster = [self.order_cluster.item(l).data(Qt.UserRole) for l in range(self.order_cluster.count())]
        self.ctx.app_data.order_diverse = [self.order_diverse.item(l).data(Qt.UserRole) for l in range(self.order_diverse.count())]

        self.ctx.set_unsaved()

    def buttonclicked_manual_add(self):
        try:
            people_list = [[i, self.ctx.__dataManager.get_print_labels(i)] for i in range(len(self.ctx.app_data.peopledata_vals)) if i not in [m[0] for m in self.ctx.app_data.manuals]]
        except Exception as e:
            QMessageBox.critical(self, "Error", "Error: {}".format(str(e)))
            return
        tables = self.ctx.app_data.settings['tables']
        status, person, table = TAManualDialog.get_input(self, people_list, tables)
        if not status: return
        self.ctx.app_data.manuals.append([person, table])
        self.update_manuals_list()
        self.ctx.set_unsaved()

    def buttonclicked_manual_del(self):
        if not self.order_manual.currentItem(): return
        index = self.order_manual.indexFromItem(self.order_manual.currentItem()).row()
        self.ctx.app_data.manuals.pop(index)
        self.update_manuals_list()
        self.ctx.set_unsaved()

    def userchanged_settings_fields(self):
        if self._settings_being_updated: return
        try:
            self.ctx.app_data.settings['tables'] = int(self.tables_field.text()) if self.tables_field.text() else 0
            self.ctx.app_data.settings['seats'] = int(self.seats_field.text()) if self.seats_field.text() else 0
            self.ctx.app_data.settings['nallocations'] = int(self.number_field.text()) if self.number_field.text() else 0
        except Exception as e:
            QMessageBox.critical(self, "Error", "Error occurred while processing your entry: {}".format(str(e)))
        self.ctx.set_unsaved()

    def buttonclicked_advanced_settings(self):
        try:
            attempts_default = self.ctx.app_data.settings['nattempts']
            seed_default = self.ctx.app_data.settings['seed']
            status, attempts, seed = TAAdvancedSettingsDialog.get_input(self, attempts_default, seed_default)
            if not status: return
            self.ctx.app_data.settings['nattempts'] = attempts
            self.ctx.app_data.settings['seed'] = seed
        except Exception as e:
            QMessageBox.critical(self, "Error", "Error occurred while processing your entry: {}".format(str(e)))
        self.ctx.set_unsaved()

    def buttonclicked_run_allocation(self):
        attempts = self.ctx.app_data.settings['nattempts']
        progress_bar = QProgressDialog("Generating table allocations...", "", 0, attempts, self.ctx.__mainWindow)
        progress_bar.setWindowTitle("Generating...")
        progress_bar.setWindowModality(Qt.WindowModal)
        progress_bar.setAutoClose(False)
        progress_bar.setMinimumDuration(0)
        progress_bar.setCancelButton(None)

        progress_bar.show()
        progress_bar.setValue(0)

        try:
            self.ctx.allocationsManager.run(progress_bar)
        except Exception as e:
            progress_bar.close()
            QMessageBox.critical(self, "Error", "An error occured during allocation: {}".format(str(e)))
            return

        progress_bar.close()
        QMessageBox.information(self, "Success!", "The allocations were successfully computed. Average number of links is {:.2f} ({:.2f} % of max).".format(self.ctx.allocationsManager.links, 100 * self.ctx.allocationsManager.links_rel))

        self.ctx.set_unsaved()
        self.ctx.__mainWindow.__tabs.results_updated()
        self.ctx.__mainWindow.__results_menu.setEnabled(True)
