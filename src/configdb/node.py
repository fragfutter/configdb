from configdb.errors import NotALeaf

NODE_LEAVES = (bool, int, float, str)
NODE_BRANCHES = (dict, list)


class Node(object):
    """A Configuration entry. Can be a leaf or a branch.

    leaves store basic values. These are boolean int, float, str
    branches can store dictionaries or lists.

    A leave value is accessed via tha val property.

    On assigning a basic value to a branch node, all children are lost.

    Attributes:
        label: name of the node
        parent: reference to the parent node or None
        val:
            reading from leaf return value as bool, int, float, str
            reading from branches raise NotALeaf Exception
            assigning stores a value and cleans up children.

    """
    def __init__(self, label, parent=None, value=None):
        self._val = {}
        self._parent = None
        self.label = label
        self.parent = parent
        self.val = value
        self.children = []

    @property
    def is_leave(self):
        return isinstance(self._val, NODE_LEAVES)

    @property
    def is_branch(self):
        return isinstance(self._val, NODE_BRANCHES)

    @property
    def is_list(self):
        return isinstance(self._val, list)

    @property
    def val(self):
        if self.is_leave:
            return self._val
        else:
            raise NotALeaf()

    @val.setter
    def val(self, data):
        self.children = []
        if data is None:
            self._val = {}
            return
        if isinstance(data, NODE_LEAVES):
            self._val = data
        else:
            raise NotALeaf()

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, data):
        if self._parent and self in self._parent.children:
            # remove from old parent
            self._parent.children.remove(self)
        if data:
            # add to new parent
            data.children.append(self)
        self._parent = data

    def pickle(self, data):
        """recursively store given data structure starting with self

        Args:
            data: data structure { "key": "value", "nested: { "key": "value" } }
        """
        try:
            self.val = data
            return
        except NotALeaf:
            pass
        if isinstance(data, list):
            self._val = []  # remember type
            data = zip(range(len(data)), data)
        if isinstance(data, dict):
            self._val = {}  # remember type
            data = data.items()
        for index, value in data:
            n = Node(str(index), parent=self)
            n.pickle(value)

    def unpickle(self, limit=None):
        """recursively retrieve data from self

        Args:
            limit (int): optional recursion limit
        Returns:
            data structure, { "key": "value", "nested: { "key": "value" } }
        """
        try:
            return self.val
        except NotALeaf:
            pass
        result = {}
        for child in self.children:
            result[child.label] = child.unpickle()
        if self.is_list:
            result = [result[i] for i in sorted(result)]
        return result

    def child(self, label, create=False):
        """return child by label

        Args:
            create (bool): autocreate child
        """
        for child in self.children:
            if child.label == label:
                return child
        if create:
            child = Node(label, parent=self)
            return child
        return None

    @classmethod
    def by_path(cls, path, create=False):
        """retrieve Node by path

        Args:
            path (str): slash seperated path to node
            create (bool): automaticly create any missing node
        """
        parent = ROOT
        if not path:
            return parent
        for element in filter(None, path.split('/')):
            if not parent.is_branch:
                raise Exception("path %s contains leaf element %s" % (path, parent.label))
            node = parent.child(element, create=create)
            if not node:
                return None
            parent = node
        return parent

    @property
    def path(self):
        """the node path as a string"""
        return '/'.join(filter(None, map(lambda x: x.label, self.xpath)))

    @property
    def xpath(self):
        """a list of nodes starting at root, leading to self"""
        result = []
        node = self
        while node:
            result.append(node)
            node = node.parent
        result.reverse()
        print(result)
        return result


ROOT = Node('')

if __name__ == '__main__':
    x = Node.by_path('/foo/bar', create=True)
    y = Node.by_path('/foo/list', create=True)
    y.pickle(['eins', 'zwei', 'drei'])
    Node.by_path('/foo/list/2').val = 'DREI'
    print(ROOT.unpickle())
