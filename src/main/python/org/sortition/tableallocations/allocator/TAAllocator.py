import copy

### class for all the allocations stuff
class TAAllocator:
    def __init__(self, tables, seats, people, cats_cluster, cats_diverse):
        self.tables = tables
        self.seats = seats

        self.people = people

        self.cats_cluster = self._get_fields_order(cats_cluster)
        self.cats_diverse = self._get_fields_order(cats_diverse)

        self.manuals = []
        self.template = [[None for s in range(self.seats)] for r in range(self.tables)]

    def set_manually(self, manuals):
        self.manuals = manuals
        for pid, t in manuals:
            ss = min(s for s in range(self.seats) if not self.template[t][s])
            self.template[t][ss] = [pid, self.people[pid]]

    ### actually run the calculation for given tables, seats, and input data
    def run(self, pids_shuffled):
        self.already_allocated = []
        self.allocations = copy.deepcopy(self.template)

        self._pids_ordered = self._order_people_iteratively(pids_shuffled, [cat_key for cat_key in {**self.cats_cluster, **self.cats_diverse}])

        for pid in self._pids_ordered:
            if pid in self.manuals: continue
            pdetails = self.people[pid]
            self._allocate_person(pid, pdetails)
            self.already_allocated.append(pid)

        return self.allocations

    ### order people iteratively by sub-categories
    def _order_people_iteratively(self, pids, cat_keys):
        if not cat_keys: return pids

        cat_key = cat_keys[0]
        people_ret = []
        for cat_val in {**self.cats_cluster, **self.cats_diverse}[cat_key]:
            people_ret.append(self._order_people_iteratively([pid for pid in pids if self.people[pid][cat_key]==cat_val], cat_keys[1:]))

        return [item for sublist in sorted(people_ret, key=len) for item in sublist]

    ### allocate a person a seat
    def _allocate_person(self, pid, pdetails):
        tablelist = [t for t in range(self.tables) if self.allocations[t].count(None) > 0]

        supfield_filters = {}
        for cat_key in self.cats_cluster:
            cat_val = pdetails[cat_key]
            if(cat_val == self.cats_cluster[cat_key][-1]): continue
            cat_counts = [[t,self._count_categories(t, cat_key, cat_val)] for t in tablelist]
            tablelist_tmp = [t for t in tablelist if next(entry[1] for entry in cat_counts if entry[0]==t)>=1]
            seats_required = self._number_of_people_filtered(cat_key, cat_val, supfield_filters)
            while sum(self.allocations[t].count(None) for t in tablelist_tmp) < seats_required:
                tableoptions = [t for t in tablelist if t not in tablelist_tmp]
                tableoptions.sort(key=lambda t: sum(1 for person in self.allocations[t] if person and person[1][cat_key] != cat_val))
                tablelist_tmp.append(tableoptions.pop(0))
            tablelist = tablelist_tmp
            supfield_filters[cat_key] = cat_val

        #tablelist = [t for t in tablelist if self.allocations[t].count(None) > 0]

        for cat_key in self.cats_diverse:
            cat_val = pdetails[cat_key]
            cat_counts = [[t,self._count_categories(t, cat_key, cat_val)] for t in tablelist]
            cat_countsmin = min(cat_counts, key=lambda x: x[1])[1]
            tablelist = [t for t in tablelist if next(entry[1] for entry in cat_counts if entry[0]==t)==cat_countsmin]

        tt = tablelist.pop()
        ss = min(s for s in range(self.seats) if not self.allocations[tt][s])

        self.allocations[tt][ss] = [pid, pdetails]

        return

    ### count number of occurences of a categorie value on table t
    def _count_categories(self, t, field_key, field_val):
        return len([p for p in self.allocations[t] if p and p[1][field_key]==field_val])

    ### get total number of pids in people array with field_key set to a specific field_val
    def _number_of_people(self, field_key, field_val):
        return sum(1 for person in self.people if person[field_key] == field_val)

    def _number_of_people_filtered(self, field_key, field_val, supfield_filters):
        pids = self._pids_ordered[:]

        for supfield_key, supfield_val in supfield_filters.items():
            pids = [pid for pid in pids if self.people[pid][supfield_key] == supfield_val]

        return sum(1 for pid in pids if self.people[pid][field_key] == field_val and not pid in self.already_allocated)

    ### return the field values sorted by their number of occurence
    def _get_field_vals_ordered(self, field_key, field_vals):
        return sorted(field_vals, key=lambda field_val: self._number_of_people(field_key, field_val))

    def _get_fields_order(self, fields):
        return {field_key: self._get_field_vals_ordered(field_key, fields[field_key]) for field_key in fields}
