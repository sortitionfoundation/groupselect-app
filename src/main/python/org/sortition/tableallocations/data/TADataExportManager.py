class TADataExportManager:
    def __init__(self, ctx):
        self.ctx = ctx

    def get_fname(self):
        return self._fname

    def set_fname(fname):
        self._fname = fname

    def isset_fname(self):
        return True if self._fname else False

    def load(self):
        with open(self._fname, 'r') as fhandle:
            new_app_data = jsonpickle.decode(fhandle.read())
        self.ctx.app_data = new_app_data

    def load_fname(self, fname):
        self.set_fname(fname)
        self.load()

    def save():
        with open(self._fname, 'w') as fhandle:
            fhandle.write(jsonpickle.encode(self.ctx.app_data))

    def save_fname(self, fname):
        self.set_fname(fname)
        self.save()

