import random

from org.sortition.groupselect.allocator.TAAllocator import TAAllocator

class TAAllocationsManager:
    def __init__(self, ctx):
        self.ctx = ctx

    def run(self, progress_bar=None):
        app_data = self.ctx.app_data

        tables = app_data.settings['tables']
        seats = app_data.settings['seats']

        if(tables*seats < len(app_data.peopledata_vals)):
            raise Exception("Error: Not enough space!", "There's not enough space! Please increase the number of groups or number of people per group!")

        seed = app_data.settings['seed']

        try:
            random.seed(seed)
        except:
            raise Exception("Error: Random seed incorrect!", "There was a problem setting the random seed. Please check your input!")

        nallocations = app_data.settings['nallocations']
        nattempts = app_data.settings['nattempts']

        peopledata_vals_used = [{} for i in range(app_data.m_data)]

        for i in range(app_data.m_data):
            for j in app_data.order_cluster+app_data.order_diverse:
                peopledata_vals_used[i][j] = self.ctx.app_data_manager.load_details(i, j)

        order_cluster_dict = self.ctx.app_data_manager.get_fields_cluster_dict()
        order_diverse_dict = self.ctx.app_data_manager.get_fields_diverse_dict()

        if not order_diverse_dict:
            raise Exception("Error: One diversification field required!", "You have to set at least one field that is used to diversify people across groups.")

        allocator = TAAllocator(tables, seats, peopledata_vals_used, order_cluster_dict, order_diverse_dict)

        manuals = app_data.manuals

        if any([len([m[0] for m in manuals if m[1] == t]) > seats for t in range(tables)]):
            raise Exception("Error: Too many manuals!", "You allocated too many people manually to one group.")
        allocator.set_manually(manuals)

        allocations = []
        pids = list(range(len(app_data.peopledata_vals)))
        for n in range(nattempts):
            if progress_bar: progress_bar.setValue(n+1)
            random.shuffle(pids)
            result = allocator.run(pids)
            allocations.append([[person[0] for person in table if person] for table in result])

        allocation_groups = []
        for n in range(nattempts):
            allocation_group = random.sample(allocations, nallocations)
            allocation_group_links = 0
            allocation_group_links_max = 0

            for pid in range(app_data.m_data):
                links = []
                for allc in allocation_group:
                    for t in range(tables):
                        if pid in allc[t]:
                            new_links = allc[t][:]
                            new_links.remove(pid)
                            links.extend(new_links)
                            allocation_group_links_max += len(allc[t])-1
                allocation_group_links += len(list(set(links)))

            allocation_groups.append([allocation_group_links, allocation_group_links_max, allocation_group])

        allcmax = max(allocation_groups, key=lambda x: x[0])
        allocation_group_outcome = allcmax[2]
        allocation_group_links_pp = allcmax[0]/app_data.m_data
        allocation_group_links_pp_max = allcmax[1]/app_data.m_data

        self.ctx.app_data.results = allocation_group_outcome

        self.links = allocation_group_links_pp
        self.links_rel = allocation_group_links_pp/allocation_group_links_pp_max
