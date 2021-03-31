from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QLineEdit, \
    QListWidget, QGroupBox, QGridLayout, QFormLayout, QListWidgetItem, QProgressDialog, QListView
from PyQt5.QtGui import QIntValidator

from org.sortition.groupselect.gui.maintabs.generate.TAManualDialog import TAManualDialog
from org.sortition.groupselect.gui.maintabs.generate.TAListMove import TAListMove
from org.sortition.groupselect.gui.maintabs.generate.TAAdvancedSettingsDialog import TAAdvancedSettingsDialog

class TAGenerateSettingsGroup(QGroupBox):
    def __init__(self, ctx):
        super(TAGenerateSettingsGroup, self).__init__("Allocation Settings")
        self.ctx = ctx

        self.__createUi()

    def __createUi(self):
        layout = QHBoxLayout()
        layout.addWidget(self.__createManualGroup(), 3)
        layout.addWidget(self.__createSettingsGroup(), 2)
        self.setLayout(layout)

    def __createManualGroup(self):
        self.orderManual = QListView()
        self.orderManual.setModel(self.ctx.getManualsModel())

        btn1 = QPushButton("Create")
        btn1.clicked.connect(self.__buttonclickedManualAdd)
        btn2 = QPushButton("Delete")
        btn2.clicked.connect(self.__buttonclickedManualDelete)

        manualButtonList = QHBoxLayout()
        manualButtonList.addWidget(btn1)
        manualButtonList.addWidget(btn2)
        manualButtonListWidget = QWidget()
        manualButtonListWidget.setLayout(manualButtonList)

        manualLayout = QVBoxLayout()
        manualLayout.addWidget(self.orderManual)
        manualLayout.addWidget(manualButtonListWidget)
        manualGroup = QGroupBox("Manual Allocation")
        manualGroup.setLayout(manualLayout)

        return manualGroup

    def __createSettingsGroup(self):
        self.seats_field = QLineEdit()
        self.seats_field.setValidator( QIntValidator(1, 16, self) )
        #self.seats_field.textChanged.connect(self.userchanged_settings_fields)

        self.tables_field = QLineEdit()
        self.tables_field.setValidator( QIntValidator(1, 100, self) )
        #self.tables_field.textChanged.connect(self.userchanged_settings_fields)

        self.number_field = QLineEdit()
        self.number_field.setValidator( QIntValidator(1, 16, self) )
        #self.number_field.textChanged.connect(self.userchanged_settings_fields)

        btnAdvanced = QPushButton("Change Settings")
        #btnAdvanced.clicked.connect(self.buttonclicked_advanced_settings)

        m = 50
        formLayout = QFormLayout()
        formLayout.setContentsMargins(m, 0, m, 0)
        formLayout.addRow(QLabel("Num. of Groups"), self.tables_field)
        formLayout.addRow(QLabel("Num. of People per Group"), self.seats_field)
        formLayout.addRow(QLabel("Number of Allocations"), self.number_field)
        formLayout.addRow(QLabel("Advanced Settings"), btnAdvanced)
        formWidget = QWidget()
        formWidget.setLayout(formLayout)

        btnRun = QPushButton("Generate Groups!")
        #btnRun.clicked.connect(self.buttonclicked_run_allocation)

        settingsLayout = QGridLayout()
        settingsLayout.addWidget(formWidget, 1, 1, 1, 1)
        settingsLayout.addWidget(btnRun, 2, 1, 1, 2)
        settingsWidget = QWidget()
        settingsWidget.setLayout(settingsLayout)

        return settingsWidget

    def __buttonclickedManualAdd(self):
        try:
            peopleList = self.orderManual.model().getSelectable()
            groupList = self.orderManual.model().getGroups()
        except Exception as e:
            QMessageBox.critical(self, "Error", "Error: {}".format(str(e)))
            return
        status, person, group = TAManualDialog.get_input(self, peopleList, groupList)
        if not status: return
        self.orderManual.model().addManual(person, group)

    def __buttonclickedManualDelete(self):
        if not self.orderManual.selectedIndexes():
            return
        self.orderManual.model().removeManual(self.orderManual.currentIndex().row())

    def update_settings(self):
        self._settings_being_updated = True

        self.tables_field.setText(str(self.ctx.app_data.settings['tables']))
        self.seats_field.setText(str(self.ctx.app_data.settings['seats']))

        self.number_field.setText(str(self.ctx.app_data.settings['nallocations']))

        self._settings_being_updated = False

    def userchanged_settings_fields(self):
        if self._settings_being_updated: return
        try:
            self.ctx.app_data.settings['tables'] = int(self.tables_field.text()) if self.tables_field.text() else 0
            self.ctx.app_data.settings['seats'] = int(self.seats_field.text()) if self.seats_field.text() else 0
            self.ctx.app_data.settings['nallocations'] = int(self.number_field.text()) if self.number_field.text() else 0
        except Exception as e:
            QMessageBox.critical(self, "Error", "Error occurred while processing your entry: {}".format(str(e)))
        self.ctx.changesToFile()

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
        self.ctx.changesToFile()

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

        self.ctx.changesToFile()
        self.ctx.__mainWindow.__tabs.results_updated()
        self.ctx.__mainWindow.__resultsMenu.setEnabled(True)