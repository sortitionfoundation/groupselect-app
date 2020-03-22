from PyQt5.QtCore import QDateTime, Qt, QTimer, QObject
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QStyleFactory, QWidget, QPushButton, QTabWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QLabel, QMessageBox, QFileDialog, QInputDialog, QLineEdit, QTableWidgetItem, QErrorMessage, QListWidget, QComboBox, QGroupBox, QGridLayout, QFormLayout, QScrollArea, QAbstractItemView, QListWidgetItem, QSizePolicy)
from PyQt5.QtGui import QIntValidator, QDoubleValidator

from org.sortition.tableallocations.gui.maintabs.results.TAListDragAndDrop import TAListDragAndDrop

class TAAllocationOutputTab(QScrollArea):
    def __init__(self, ctx, a):
        super(TAAllocationOutputTab, self).__init__()
        self.ctx = ctx
        self.a = a

        self.wgtMain = QWidget()
        self.wgtMain.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        self.hboxMain = QHBoxLayout(self.wgtMain)

        self.allocation = self.ctx.app_data.results[a]

        self.drag_lists = []
        self.labels = []
        self.wgtSubs = []
        self.wgtSubLyts = []

        for t, table in enumerate(self.allocation):
            wgtSub = QGroupBox("Table {}".format(t+1))
            wgtSub.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
            vboxSub = QVBoxLayout(wgtSub)
            self.wgtSubs.append(wgtSub)
            self.wgtSubLyts.append(vboxSub)

            drag_list = TAListDragAndDrop()
            drag_list.setMinimumHeight(200)
            drag_list.trigger.connect(self.update_tables_by_user)
            self.drag_lists.append(drag_list)
            vboxSub.addWidget(drag_list)

            label = QLabel()
            label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.labels.append(label)
            vboxSub.addWidget(label)

            self.hboxMain.addWidget(wgtSub)

        self.setWidget(self.wgtMain)

        self.set_content()

    def set_content(self):
        for t, table in enumerate(self.allocation):
            drag_list = self.drag_lists[t]
            label = self.labels[t]

            order_cluster_dict = self.ctx.app_data_manager.get_fields_cluster_dict()
            order_diverse_dict = self.ctx.app_data_manager.get_fields_diverse_dict()
            cats = {**order_cluster_dict, **order_diverse_dict}

            # set drag_list items
            drag_list.clear()
            r = 0
            for pid in table:
                newItem = QListWidgetItem()
                newItem.setData(Qt.UserRole, pid)
                print_label = self.ctx.app_data_manager.get_print_labels(pid)
                newItem.setText(print_label)
                tooltip_infos = [print_label]
                for field_key in cats:
                    field_key_label = self.ctx.app_data.peopledata_keys[field_key]
                    field_pid_val = self.ctx.app_data_manager.load_details(pid, field_key)
                    tooltip_infos.append("{}: {}".format(field_key_label, field_pid_val))
                newItem.setToolTip("\n".join(tooltip_infos))
                drag_list.insertItem(r, newItem)
                r += 1


            label_strings = ["<p><strong>Total: {}</strong></p>".format(len(table))]

            for cat_key, cat_val_terms in cats.items():
                label_strings.append("<p>{}:<br/>".format(self.ctx.app_data.peopledata_keys[cat_key]))
                label_strings_cat = []
                for cat_val_term in cat_val_terms:
                    occurences = self.ctx.app_data_manager.get_occurences(self.a, t, cat_key, cat_val_term)
                    label_strings_cat.append("{} {}".format(occurences, cat_val_term))
                label_strings.append("<br/>".join(label_strings_cat))
                label_strings.append("</p>")

            label_string = " ".join(label_strings)
            label.setText(label_string)

        self.wgtMain.resize(self.hboxMain.sizeHint().width(),self.wgtSubs[0].sizeHint().height()+30)

    def update_tables_by_user(self):
        new_allocation = [[] for t in self.allocation]

        for t, table in enumerate(self.allocation):
            new_allocation[t] = [self.drag_lists[t].item(i).data(Qt.UserRole) for i in range(self.drag_lists[t].count())]

        self.ctx.app_data.results[self.a] = new_allocation
        self.allocation = new_allocation

        self.ctx.set_unsaved()

        self.set_content()
