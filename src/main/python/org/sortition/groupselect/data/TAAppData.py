class TAAppData:
    def __init__(self):
        self.peopledata_keys = []
        self.peopledata_vals = []
        self.peopledata_terms = []

        self.fields = {}

        self.settings = {'tables': 6, 'seats': 8, 'nallocations': 3, 'nattempts': 100, 'seed': 1.0}

        self.order_cluster = []
        self.order_diverse = []
        self.manuals = []

        self.results = []
