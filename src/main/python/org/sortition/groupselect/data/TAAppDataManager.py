from org.sortition.groupselect.data.TAAppData import TAAppData
from org.sortition.groupselect.data.TAFileSaveManager import TAFileSaveManager

from org.sortition.groupselect.data.models.TAPeopleDataModel import TAPeopleDataModel
from org.sortition.groupselect.data.models.TAFieldsListModel import TAFieldsListModel
from org.sortition.groupselect.data.models.TASettingsDataModel import TASettingsDataModel
from org.sortition.groupselect.data.models.TATermsDataModel import TATermsDataModel
from org.sortition.groupselect.data.models.TAFieldsStringListModel import TAFieldsStringListModel
from org.sortition.groupselect.gui.maintabs.generate.TAManualsListModel import TAManualsListModel

import csv


class TAAppDataManager:
    def __init__(self, ctx: 'AppContext'):
        self.ctx = ctx

        self.currentAppData = None

        self.settingsDataModel = TASettingsDataModel()

        self.peopleDataModel = TAPeopleDataModel()
        self.fieldsListModel = TAFieldsListModel()
        self.termsDataModel = TATermsDataModel()

        self.__fieldModeModels = {}
        for mode in ['ignore', 'print', 'cluster', 'diverse']:
            self.__fieldModeModels[mode] = TAFieldsStringListModel(mode)

        self.__manualsModel = TAManualsListModel(self)

        self.__filesaveManager = TAFileSaveManager()

        self.__connectModels()

    def __connectModels(self):
        # record new changes to file
        self.peopleDataModel.dataChanged.connect(self.ctx.changesToFile)
        self.peopleDataModel.layoutChanged.connect(self.ctx.changesToFile)
        self.termsDataModel.dataChanged.connect(self.ctx.changesToFile)
        self.termsDataModel.layoutChanged.connect(self.ctx.changesToFile)

        for mode in self.__fieldModeModels:
            self.__fieldModeModels[mode].dataChanged.connect(self.ctx.changesToFile)
            self.__fieldModeModels[mode].layoutChanged.connect(self.ctx.changesToFile)

        self.__manualsModel.dataChanged.connect(self.ctx.changesToFile)

        # updates arising from new people data
        self.peopleDataModel.dataChanged.connect(self.__peopleDataUpdated)
        self.peopleDataModel.layoutChanged.connect(self.__peopleDataUpdated)

    def updateAppData(self):
        # tell all models that a new appData object is being used
        self.settingsDataModel.updateAppData(self.currentAppData)

        self.peopleDataModel.updateAppData(self.currentAppData)
        self.fieldsListModel.updateAppData(self.currentAppData)
        self.termsDataModel.updateAppData(self.currentAppData)

        for mode in self.__fieldModeModels:
            self.__fieldModeModels[mode].updateAppData(self.currentAppData)

        self.__manualsModel.updateAppData(self.currentAppData)

    def __peopleDataUpdated(self):
        self.termsDataModel.updatedPeopleData()
        self.__updateFieldsFromKeys()

    def __updateFieldsFromKeys(self):
        m_data = len(self.currentAppData.peopledata_keys)
        allFields = list(range(0, m_data))

        currentFields = []
        for mode in self.__fieldModeModels:
            currentFields.extend(self.currentAppData.fieldsUsage[mode])

        for f in allFields:
            if f not in currentFields:
                self.currentAppData.fieldsUsage['ignore'].append(f)

        for f in currentFields:
            if f not in allFields:
                currentFields.remove(f)

        for mode in self.__fieldModeModels:
            self.__fieldModeModels[mode].stringListUpdated()

    ### global commands
    def appStart(self):
        self.closeFile()

    def newFile(self, number, names):
        self.generate_empty()
        self.updateAppData()
        self.__filesaveManager.unsetFname()
        self.peopleDataModel.generateNewData(number, names)

    def closeFile(self):
        self.generate_empty()
        self.updateAppData()
        self.__filesaveManager.unsetFname()

    def loadFile(self, fname):
        ex, app_data = self.__filesaveManager.load_fname(fname)

        if ex: return ex
        else:
            self.currentAppData = app_data
            self.updateAppData()

    def saveFile(self, fname):
        ex = self.__filesaveManager.save_fname(self.currentAppData, fname)

        if ex: return ex

    def getFname(self):
        return self.__filesaveManager.getFname()

    def issetFname(self):
        return self.__filesaveManager.issetFname()

    def setFieldsView(self, view_state):
        self.peopleDataModel.setFieldsView(view_state)

    def getFieldsModels(self):
        return self.__fieldModeModels

    def getManualsModel(self):
        return self.__manualsModel

    ### generate or load appdata
    def generate_empty(self):
        self.currentAppData = TAAppData()

    ### getters and setters
    def hasPeople(self):
        return not self.peopleDataModel.isEmpty()

    def hasResults(self):
        return True if self.currentAppData.results else False

    def get_fields_with_mode(self, mode: str):
        return self.currentAppData.fieldsUsage[mode]

    def get_print_labels(self, pid, include_pid = False):
        print_fields = self.get_fields_with_mode('print')
        if not print_fields: return "Person {0}".format(pid + 1)
        retvals = []
        for j in print_fields:
            retvals.append(self.currentAppData.peopledata_vals[pid][j])
        retval = " ".join(retvals) if any(retvals) else "(empty print label)"
        if include_pid: retval += " (ID {0})".format(pid + 1)
        return retval

    def get_group_label(self, gid):
        return "Group {0}".format(gid+1)

    def get_fields_cluster_dict(self):
        return {j:list(set([t_used for t_found, t_used in self.ctx.app_data.fields[j]['terms']])) for j in self.ctx.app_data.order_cluster}

    def get_fields_diverse_dict(self):
        return {j:list(set([t_used for t_found, t_used in self.ctx.app_data.fields[j]['terms']])) for j in self.ctx.app_data.order_diverse}

    def load_details(self, i, j):
        try:
            r = next(t_used for t_found, t_used in self.ctx.app_data.fields[j]['terms'] if t_found == self.ctx.app_data.peopledata_vals[i][j])
        except StopIteration:
            raise Exception(f"There was an issue finding the terms used in field \'{self.ctx.app_data.peopledata_keys[j]}\'. Please go back to the fields tab and make sure all fields are correctly defined.")
        if r == "": return "(empty term)"
        return r

    def get_occurences(self, a, t, j, t_used):
        return sum(1 for i in self.ctx.app_data.results[a][t] if self.load_details(i, j) == t_used)

    def cols_not_ignored(self, cols):
        return any((j in self.ctx.app_data.fields and self.ctx.app_data.fields[j]['mode'] != 'ignore') for j in cols)

    def export_raw_to_csv(self, file_handle):
        app_data = self.ctx.app_data
        writer = csv.writer(file_handle, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(app_data.peopledata_keys)
        for entry in app_data.peopledata_vals:
            writer.writerow(entry)

    def export_allocation_to_csv(self, file_handle, a):
        allocation = self.ctx.app_data.results[a]
        writer = csv.writer(file_handle, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        header = ['Person/Group']
        numTables = len(allocation)
        numMaxSeats = max(len(table) for table in allocation)
        for t in range(numTables):
            header.append(str(t+1))
        writer.writerow(header)
        for s in range(numMaxSeats):
            row = [str(s+1)]
            for t in range (numTables):
                if s < len(allocation[t]): row.append(self.get_print_labels(allocation[t][s]))
                else: row.append("(empty)")
            writer.writerow(row)
        writer.writerow([''] + numTables*["--------"])
        writer.writerow([''] + ["Total: {}".format(len(table)) for table in allocation])
        cats = {**self.get_fields_cluster_dict(), **self.get_fields_diverse_dict()}
        for cat_key, cat_val_terms in cats.items():
            writer.writerow([''] + numTables*["--------"])
            writer.writerow([''] + numTables*["{}:".format(self.ctx.app_data.peopledata_keys[cat_key])])
            for cat_index, cat_val_term in enumerate(cat_val_terms):
                writer.writerow([str(cat_index+1)] + ["{} {}".format(self.get_occurences(a, t, cat_key, cat_val_term), cat_val_term) for t in range(numTables)])

    def insert_rows(self, beforeRow, number):
        self.ctx.app_data.m_data += number

        for n in range(number):
            self.ctx.app_data.peopledata_vals.insert(beforeRow, ['' for j in range(self.ctx.app_data.n_data)])

        for manual in self.ctx.app_data.manuals:
            pid = manual[0]
            if(pid >= beforeRow):
                manual[0] = pid + number

        self.ctx.app_data.results = []

    def insert_cols(self, beforeCol, number):
        self.ctx.app_data.n_data += number

        for n in range(number):
            self.ctx.app_data.peopledata_keys.insert(beforeCol+n, f"New column {n+1}" if number>1 else "New column")

            for person in self.ctx.app_data.peopledata_vals:
                person.insert(beforeCol+n, "")

        new_fields = {}
        for j in self.ctx.app_data.fields:
            j_new = j+number if j >= beforeCol else j
            new_fields[j_new] = self.ctx.app_data.fields[j]
        self.ctx.app_data.fields = new_fields

        for k in range(len(self.ctx.app_data.order_cluster)):
            j = self.ctx.app_data.order_cluster[k]
            if(j >= beforeCol): self.ctx.app_data.order_cluster[k] = j + number

        for k in range(len(self.ctx.app_data.order_diverse)):
            j = self.ctx.app_data.order_diverse[k]
            if(j >= beforeCol): self.ctx.app_data.order_diverse[k] = j + number

    def delete_rows(self, rows):
        self.ctx.app_data.m_data -= len(rows)

        self.ctx.app_data.peopledata_vals = [vals for i, vals in enumerate(self.ctx.app_data.peopledata_vals) if i not in rows]

        self.ctx.app_data.manuals = [manual for manual in self.ctx.app_data.manuals if manual[0] not in rows]

        for manual in self.ctx.app_data.manuals:
            pid = manual[0]
            decrement = sum(1 for row in rows if pid > row)
            manual[0] = pid - decrement

        self.ctx.app_data.results = []

    def delete_cols(self, cols, must_discard_results=False):
        self.ctx.app_data.n_data -= len(cols)

        self.ctx.app_data.peopledata_keys = [key for j, key in enumerate(self.ctx.app_data.peopledata_keys) if j not in cols]

        for pid in range(self.ctx.app_data.m_data):
            entry = self.ctx.app_data.peopledata_vals[pid]
            new_entry = [val for j, val in enumerate(entry) if j not in cols]
            self.ctx.app_data.peopledata_vals[pid] = new_entry

        new_fields = {}
        for j in self.ctx.app_data.fields:
            if j in cols: continue
            decrement = sum(1 for j2 in cols if j > j2)
            new_fields[j-decrement] = self.ctx.app_data.fields[j]
        self.ctx.app_data.fields = new_fields

        self.ctx.app_data.order_cluster = [j for j in self.ctx.app_data.order_cluster if j not in cols]
        for k in range(len(self.ctx.app_data.order_cluster)):
            j = self.ctx.app_data.order_cluster[k]
            decrement = sum(1 for j2 in cols if j > j2)
            self.ctx.app_data.order_cluster[k] = j - decrement

        self.ctx.app_data.order_diverse = [j for j in self.ctx.app_data.order_diverse if j not in cols]
        for k in range(len(self.ctx.app_data.order_diverse)):
            j = self.ctx.app_data.order_diverse[k]
            decrement = sum(1 for j2 in cols if j > j2)
            self.ctx.app_data.order_diverse[k] = j - decrement

        if must_discard_results:
            self.ctx.app_data.results = []
