import re

pat_prop = re.compile('\s*([^#!:=]+)(?:\s*[\s=:]\s*)(.+$)')


class PropertyParser(object):
    def __init__(self, data=None):
        self.data = data

    def load(self, data):
        """load data from string"""
        self.data = None
        # TODO find or write a save properties parser
        self.data = {}
        # replace escaped newlines
        data = data.replace('\\\n', ' ')
        for line in data.split('\n'):
            line = line.strip()
            m = pat_prop.match(line)
            if m:
                key, val = map(lambda x: x.strip(), m.groups())
                val = self.cast(val)
                node = self.data
                for element in key.split('.')[:-1]:
                    try:
                        assert(isinstance(node[element], dict))
                    except (KeyError, AssertionError):
                        node[element] = {}
                    node = node[element]
                node[key.split('.')[-1]] = val
        # recreate lists
        self.data = self._makelist(self.data)

    @classmethod
    def _makelist(cls, node):
        """recursively convert nodes to arrays.

        a node is considered an array if it is a dictionary, contains the key '0'
        and all keys are numeric"""
        if isinstance(node, dict) and '0' in node.keys():
            try:
                tmp = map(lambda x: (int(x[0]), x[1]), node.items())
                return [cls._makelist(x[1]) for x in sorted(tmp)]
            except ValueError:
                pass
        if isinstance(node, list):
            return map(cls._makelist, node)
        if isinstance(node, dict):
            return dict(map(lambda x: (x[0], cls._makelist(x[1])), node.items()))
        return node

    def dump(self):
        """dump data as properties"""
        result = []

        def pjoin(*args):
            return '.'.join(filter(None, args))

        def visit(prefix, data):
            if isinstance(data, dict):
                for k, v in sorted(data.items()):
                    visit(pjoin(prefix, k), v)
            elif isinstance(data, (list, set)):
                for index in range(len(data)):
                    visit(pjoin(prefix, str(index)), data[index])
            elif isinstance(data, (bool)):
                result.append('%s = %s' % (prefix, 'true' if data else 'false'))
            elif isinstance(data, (int, float)):
                result.append('%s = %s' % (prefix, data))
            else:
                result.append('%s = "%s"' % (prefix, data))

        visit('', self.data)
        return '\n'.join(result)

    @classmethod
    def cast(cls, value):
        """try to typecase a value"""
        value = value.strip()
        if value in ('T', 't', 'Y', 'y', 'True', 'true', 'Yes', 'yes'):
            return True
        if value in ('F', 'f', 'N', 'n', 'False', 'false', 'No', 'no'):
            return False
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        # remove leading and tailing quotes for strings
        try:
            if value[0] in ('\'', '"') and value[0] == value[-1]:
                return value[1:-1]
        except IndexError:
            pass
        return value


if __name__ == '__main__':
    p = PropertyParser()
    data = """
    foo.bar = 42
    nested.array.0 = "a0"
    nested.array.1 = "a1"
    nested.array.2 = "a3"
    pi = 3.141
    a = "the beginning \
        is here"
    """
    p.load(data)
    print(p.data)
    print(p.dump())
