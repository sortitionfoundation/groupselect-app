from org.sortition.tableallocations.data.TAAppData import TAAppData

import jsonpickle

class TAFileSaveManager:
    def __init__(self, ctx):
        self.ctx = ctx
        self._fname = None

    def get_fname(self):
        return self._fname

    def set_fname(self, fname):
        self._fname = fname

    def unset_fname(self):
        self._fname = None

    def isset_fname(self):
        return True if self._fname else False

    def new(self):
        self.ctx.app_data = TAAppData()
        self.ctx.app_data_manager.generate_empty()
        self.unset_fname()

    def close(self):
        self.ctx.app_data = TAAppData()
        self.unset_fname()

    def load(self):
        with open(self._fname, 'r') as fhandle:
            new_app_data = jsonpickle.decode(fhandle.read())
        self.ctx.app_data = new_app_data
        self.ctx.app_data.fields = {int(key):value for key,value in new_app_data.fields.items()}

    def load_fname(self, fname):
        self.set_fname(fname)
        self.load()

    def save(self):
        with open(self._fname, 'w') as fhandle:
            fhandle.write(jsonpickle.encode(self.ctx.app_data))

    def save_fname(self, fname):
        self.set_fname(fname)
        self.save()

