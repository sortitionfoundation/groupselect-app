from org.sortition.groupselect.allocator.TAAllocationsManager import TAAllocationsManager
from org.sortition.groupselect.data.TAAppData import TAAppData
from org.sortition.groupselect.data.TAFileSaveManager import TAFileSaveManager

from org.sortition.groupselect.data.models.TAPeopleDataModel import TAPeopleDataModel
from org.sortition.groupselect.data.models.TAFieldsListModel import TAFieldsListModel
from org.sortition.groupselect.data.models.TATermsDataModel import TATermsDataModel

import csv


class TAAppDataManager:
    def __init__(self, ctx:'AppContext'):
        self.ctx = ctx

        self.currentAppData = None

        self.peopleDataModel = TAPeopleDataModel()
        self.fieldsListModel = TAFieldsListModel()
        self.termsDataModel = TATermsDataModel()

        self.__filesaveManager = TAFileSaveManager()

        self.connectModels()

    def connectModels(self):
        self.peopleDataModel.dataChanged.connect(self.updatedPeopleData)

        self.peopleDataModel.dataChanged.connect(self.ctx.setUnsaved)
        self.fieldsListModel.dataChanged.connect(self.ctx.setUnsaved)
        self.termsDataModel.dataChanged.connect(self.ctx.setUnsaved)

    def updateAppData(self):
        self.peopleDataModel.updateAppData(self.currentAppData)
        self.fieldsListModel.updateAppData(self.currentAppData)
        self.termsDataModel.updateAppData(self.currentAppData)

    def updatedPeopleData(self):
        self.termsDataModel.updatedPeopleData()

    ### global commands
    def appStart(self):
        self.closeFile()

    def newFile(self):
        self.generate_new()
        self.updateAppData()
        self.__filesaveManager.unsetFname()

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

    ### generate or load appdata
    def generate_empty(self):
        self.currentAppData = TAAppData()

    def generate_new(self):
        self.currentAppData = TAAppData()

        m_data = 20
        n_data = 10

        self.currentAppData.peopledata_keys = ["Col {}".format(j+1) for j in range(n_data)]
        self.currentAppData.peopledata_vals = [['' for j in range(n_data)] for i in range(m_data)]
        self.currentAppData.peopledata_terms = [None for j in range(n_data)]

    ### getters and setters
    def hasResults(self):
        return True if self.currentAppData.results else False

    def get_fields_with_mode(self, mode):
        return [j for j, field in self.ctx.app_data.fields.items() if field['mode'] == mode]

    def get_print_labels(self, i):
        print_fields = self.get_fields_with_mode('print')
        if not print_fields: return str(i)
        rs = []
        for j in print_fields:
            rs.append(self.ctx.app_data.peopledata_vals[i][j])
        return " ".join(rs) if any(rs) else "(empty print label)"

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

    def peopledata_is_empty(self):
        return not any(self.ctx.app_data.peopledata_vals[i][j] for j in range(self.ctx.app_data.n_data) for i in range(self.ctx.app_data.m_data))

    def cols_not_ignored(self, cols):
        return any((j in self.ctx.app_data.fields and self.ctx.app_data.fields[j]['mode'] != 'ignore') for j in cols)

    ### advanced manipulation functions ###
    def import_raw_from_csv(self, file_handle, csv_format):
        app_data = self.ctx.app_data
        if(csv_format == 'auto'):
            N=10
            file_content = "".join([next(file_handle) for i in range(N)])
            ncs = file_content[:4096].count(',')
            nss = file_content[:4096].count(';')
            if(ncs < nss): csv_format = 'semicolon'
            else: csv_format = 'comma'
            file_handle.seek(0)
        csv_reader = csv.reader(file_handle, delimiter=(';' if csv_format=='semicolon' else ','))
        app_data.peopledata_keys = list(next(csv_reader))
        app_data.n_data = len(app_data.peopledata_keys)
        entries = []
        for row_raw in csv_reader:
            entries.append(row_raw)
        app_data.peopledata_vals = entries
        app_data.m_data = len(app_data.peopledata_vals)

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
