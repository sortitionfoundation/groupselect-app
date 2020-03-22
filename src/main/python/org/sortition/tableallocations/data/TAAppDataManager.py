import typing, csv

class TAAppDataManager:
    def __init__(self, ctx):
        self.ctx = ctx

    def generate_empty(self):
        app_data = self.ctx.app_data

        app_data.m_data = 20
        app_data.n_data = 10

        app_data.peopledata_keys = ["Col {}".format(j+1) for j in range(app_data.n_data)]
        app_data.peopledata_vals = [['' for j in range(app_data.n_data)] for i in range(app_data.m_data)]

        app_data.fields = {}

        app_data.settings = {'tables': 6, 'seats': 8, 'nallocations': 3, 'nattempts': 100, 'seed': 1.0}

        app_data.order_cluster = []
        app_data.order_diverse = []
        app_data.manuals = []

        app_data.results = []

    def get_terms(self, j):
        return sorted(list(set(self.ctx.app_data.peopledata_vals[i][j] for i in range(self.ctx.app_data.m_data))))

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
        return next(t_used for t_found, t_used in self.ctx.app_data.fields[j]['terms'] if t_found == self.ctx.app_data.peopledata_vals[i][j])

    def get_occurences(self, a, t, j, t_used):
        return sum(1 for i in self.ctx.app_data.results[a][t] if self.load_details(i, j) == t_used)

    def peopledata_is_empty(self):
        return not any(self.ctx.app_data.peopledata_vals[i][j] for j in range(self.ctx.app_data.n_data) for i in range(self.ctx.app_data.m_data))

    def import_raw_from_csv(self, file_handle):
        app_data = self.ctx.app_data
        csv_reader = csv.reader(file_handle, delimiter=",")
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

    def exportAllocationToCSV(self, file_handle, a):
        allocation = self.ctx.app_data.results[a]
        writer = csv.writer(file_handle, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        header = ['Seat/Table']
        numTables = len(allocation)
        numMaxSeats = max(len(table) for table in allocation)
        for t in range(numTables):
            header.append(str(t+1))
        writer.writerow(header)
        for s in range(numMaxSeats):
            row = []
            for t in range (numTables):
                if s < len(allocation[t]): row.append(self.get_print_labels(allocation[t][s][0]))
                else: row.append("(empty)")
            writer.writerow(row)
        writer.writerow((numTables+1)*["--------"])
        writer.writerow(["Total: {}".format(len(table)) for table in allocation])
        cats = dict(self.get_fields_cluster_dict(), **self.get_fields_diverse_dict())
        for cat_key, cat_val_terms in cats.items():
            writer.writerow((numTables+1)*["--------"])
            writer.writerow((numTables+1)*["{}:".format(cat_key)])
            for cat_val_term in cat_val_terms:
                writer.writerow(["{} {}".format(self.get_occurences(a, t, cat_key, cat_val_term), cat_val_term) for t in range(numTables)])
