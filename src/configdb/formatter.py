from configdb.schema import Node
from configdb.errors import DecodeException, InvalidPath
import json
import yaml


class Formatter(object):
    def __init__(self):
        self.data = None

    @classmethod
    def load_node(cls, node):
        if node.children:
            result = {}
            for child in node.children:
                result[child.label] = cls.load_node(child)
            if node.type == 'list':
                # drop indices and convert to list
                result = [result[i] for i in sorted(result)]
        else:
            result = node.val
        return result

    def load(self, path):
        """load data from database"""
        self.data = None
        node = Node.get_by_path(path)
        if not node:
            raise InvalidPath("path %s does not exist" % path)
        self.data = self.load_node(node)

    @property
    def json(self):
        return json.dumps(self.data, indent=2)

    @json.setter
    def json(self, data):
        try:
            self.data = json.loads(data)
        except json.JSONDecodeError as e:
            raise DecodeException(e)

    @property
    def yaml(self):
        return yaml.dump(self.data)

    @yaml.setter
    def yaml(self, data):
        try:
            self.data = yaml.load(data)
        except yaml.scanner.ScannerError as e:
            raise DecodeException(e)

    @property
    def prop(self):
        pass

    @prop.setter
    def prop(self, data):
        pass

    @property
    def ini(self):
        pass

    @ini.setter
    def ini(self, data):
        pass
