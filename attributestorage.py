import random
import json
import jinja2

class MaximumSequenceNumberExceeded(Exception):
    def __init__(self, maximum):
        self.maximum = maximum


class AttributeStorage:
    def __init__(self, config=None):
        self.isUpdated = False
        self.config = config
        self.data = {}

        for storage_type, storage_config in config.items():
            if storage_type == 'sequences':
                self.initializeSequences(storage_config)
            if storage_type == 'database':
                self.ReadFromDB(storage_config)
            if storage_type == 'file':
                self.ReadFromFile(storage_config)


    def initializeSequences(self, sequences):
        data = {'data': {'sequences': {}}}
        data_inner = data['data']['sequences']
        for sequence in sequences:
            current = sequence['minimum']
            maximum = sequence['maximum']
            s = { 'current': current, 'maximum': maximum }
            data_inner[sequence['name']] = s

        self.data = self.data | data


    def ReadFromDB(self, config):
        print("Database storage has not been implemented yet.")
        return


    def ReadFromFile(self, config):
        """Given the supplied config, read the json file specified therein
        and return a dictionary. In case there is no file, or there is an
        IO error, return an empty dictionary."""
        if not config['path']:
            return

        try:
            with open(config['path'], 'r') as fd:
                data = json.load(fd)
                self.data = self.data | data
        except IOError as e:
            pass


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
                    json.dump(self.data, fd, indent=2)
            except IOError as e:
                print(e)


    def AddToStorage(self, dn, attribute, values):
        if dn in self.data:
            self.data[dn][attribute] = values
            self.isUpdated = True
        else:
            self.isUpdated = True
            self.data[dn] = { attribute: values }


    def AddLiteral(self, dn, entry, attribute, values):
        try:
            existing_values = set(entry[attribute])
            new_values = set(values)
            combined_values = existing_values | new_values
            entry[attribute] = list(combined_values)
            self.AddToStorage(dn, attribute, list(new_values - existing_values))
        except KeyError:
            entry[attribute] = [values]
            self.AddToStorage(dn, attribute, values)


    def AddSequence(self, dn, entry, name):
        value = self.GetSequenceNumber(name)
        self.AddLiteral(dn, entry, name, value)


    def AddFromAttribute(self, dn, entry, attribute):
        rdn = dn.split(',')[0]
        key, value = rdn.split('=')

        context = self.data[dn]
        context = context | { key: value }

        env = jinja2.Environment()
        templ = jinja2.Template(attribute['value'])
        value = templ.render(context)

        self.AddLiteral(dn, entry, attribute['attribute'], value)


    def GetAttibuteValue(self, dn, attribute):
        return self.data[dn][attribute]


    def GetSequenceNumber(self, name):
        data = self.data['data']['sequences'][name]
        value = data['current']
        maximum = data['maximum']

        if value < maximum - 1:
            data['current'] = value + 1
        else:
            raise MaximumSequenceNumberExceeded(maximum)

        return str(value)


    def getData(self):
        return self.data
