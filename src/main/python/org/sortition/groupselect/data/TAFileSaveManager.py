import jsonpickle

class TAFileSaveManager:
    def __init__(self):
        self.__fname = None

    def getFname(self):
        return self.__fname

    def __setFname(self, fname):
        self.__fname = fname

    def unsetFname(self):
        self.__fname = None

    def issetFname(self):
        return True if self.__fname else False

    def __load(self):
        try:
            with open(self.__fname, 'r') as fhandle:
                app_data = jsonpickle.decode(fhandle.read())
        except Exception as ex:
            return ex, None

        app_data.fields = {int(key):value for key,value in app_data.fields.items()}

        return False, app_data

    def load_fname(self, __fname):
        self.__setFname(__fname)
        return self.__load()

    def __save(self, app_data):
        try:
            if not self.issetFname():
                raise Exception("Filename not set.")

            with open(self.__fname, 'w') as fhandle:
                fhandle.write(jsonpickle.encode(app_data))
        except Exception as ex:
            return ex

        return False

    def save_fname(self, app_data, fname):
        if fname: self.__setFname(fname)
        self.__save(app_data)

