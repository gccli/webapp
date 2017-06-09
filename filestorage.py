import os
import shelve

class FileStorage(object):
    def __init__(self, config):
        self.root = config['root_path']
        self.metadata = shelve.open(os.path.join(self.root, 'file.db'))

    def get_last_id(self):
        if not self.metadata.has_key('id'):
            last_id = 1
        else:
            last_id = int(self.metadata['id']) + 1

        self.metadata['id'] = str(last_id)
        self.metadata.sync()

        return self.metadata['id']

    def add(self, *args):
        last_id = self.get_last_id()
        self.metadata[last_id] = args

        return file_id

    def get(self, file_id):
        key = str(file_id)
        if not self.metadata.has_key(key):
            return None

        return self.metadata[key]
