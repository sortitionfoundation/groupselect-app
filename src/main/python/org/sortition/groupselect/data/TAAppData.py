class TAAppData:
    def __init__(self):
        self.settings = {'numGroups': 6, 'numPeoplePerGroup': 8, 'nallocations': 3, 'nattempts': 100, 'seed': 1.0}

        self.peopledata_keys = []
        self.peopledata_vals = []
        self.peopledata_terms = []

        self.fieldsUsage = {'ignore': [], 'print': [], 'cluster': [], 'diverse': []}

        self.manuals = []

        self.results = []
