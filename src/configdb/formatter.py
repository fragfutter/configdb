# from configdb.schema import Node
from configdb.node import Node
from configdb.errors import DecodeException, InvalidPath
import json
import yaml
import re
from configdb.propertyparser import PropertyParser

pat_prop = re.compile('\s*([^#!:=]+)(?:\s*[\s=:]\s*)(.*$)')


class Formatter(object):
    def __init__(self, path, create=False):
        self.node = Node.by_path(path, create=create)
        if not self.node:
            raise InvalidPath("path %s does not exist" % path)

    @property
    def json(self):
        return json.dumps(self.node.unpickle(), indent=2)

    @json.setter
    def json(self, data):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            raise DecodeException(e)
        self.node.pickle(data)

    @property
    def yaml(self):
        return yaml.dump(self.node.unpickle())

    @yaml.setter
    def yaml(self, data):
        try:
            data = yaml.load(data)
        except yaml.scanner.ScannerError as e:
            raise DecodeException(e)
        self.node.pickle(data)

    @property
    def prop(self):
        p = PropertyParser(self.node.unpickle())
        return p.dump()

    @prop.setter
    def prop(self, data):
        # TODO find or write a save properties parser
        p = PropertyParser(data)
        p.load(data)
        self.node.pickle(p.data)

    @property
    def ini(self):
        pass

    @ini.setter
    def ini(self, data):
        pass

    @property
    def value(self):
        pass
