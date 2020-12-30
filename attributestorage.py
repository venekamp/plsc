import json

class AttributeStorage:
    def __init__(self, config=None):
        self.isUpdated = False
        self.config = config

        if config is None:
            self.data = {}
            return

        for storage_type, storage_config in config.items():
            if storage_type == 'database':
                self.data = self.ReadFromDB(storage_config)
            if storage_type == 'file':
                self.data = self.ReadFromFile(storage_config)


    def ReadFromDB(self, config):
        print("Database storage has not been implemented yet.")
        return {}


    def ReadFromFile(self, config):
        if not config['path']:
            return {}

        try:
            with open(config['path'], 'r') as fd:
                return json.load(fd)
        except IOError as e:
            print(e)

        return {}


    def WriteData(self):
        for storage_type, storage_config in self.config.items():
            if storage_type == 'database':
                self.WriteToDB(storage_config)
            if storage_type == 'file':
                self.WriteToFile(storage_config)


    def WriteToDB(self, config):
        pass


    def WriteToFile(self, config):
        if self.config and self.isUpdated:
            try:
                with open(config['path'], 'w') as fd:
                    json.dump(self.data, fd)
            except IOError as e:
                print(e)


    def getData(self):
        return self.data
