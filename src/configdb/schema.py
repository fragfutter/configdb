import sqlalchemy
from configdb.meta import db
from collections import namedtuple
from configdb.errors import NotALeaf


DbType = namedtuple('DbType', ('id', 'column', 'types'))

C_DICT = DbType(0, None, (dict, ))
C_LIST = DbType(1, None, (list, tuple,))
C_BOOL = DbType(2, 'boolval', (bool, ))
C_INT = DbType(3, 'intval', (int, ))
C_FLOAT = DbType(4, 'floatval', (float, ))
C_STRING = DbType(5, 'stringval', (str, ))
C_BLOB = DbType(6, 'blobval', (type(None), ))

C_LEAVES = (C_BOOL, C_INT, C_FLOAT, C_STRING, C_BLOB)
C_BRANCHES = (C_DICT, C_LIST)


class Node(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    label = db.Column(db.String, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('node.id', ondelete='cascade'))
    children = db.relationship(
        'Node',
        backref=db.backref('parent', remote_side=[id]),
        cascade="all, delete-orphan, delete",
    )
    nodetype = db.Column(db.Integer)
    # store all variants in columns
    # alternative would be polymorphic node
    boolval = db.Column(db.Boolean)
    intval = db.Column(db.Integer)
    floatval = db.Column(db.Float)
    stringval = db.Column(db.String)
    blobval = db.Column(db.LargeBinary)
    __table_args__ = (
        db.UniqueConstraint('parent_id', 'label', name='_parent_label_uc'),
    )

    def __init__(self, label, parent=None):
        self.label = label
        self.parent = parent
        self.nodetype = 'dict'

    @property
    def val(self):
        """get node value as leaf"""
        for leaf in C_LEAVES:
            if self.nodetype == leaf.id:
                return getattr(self, leaf.column)
        raise NotALeaf()

    @val.setter
    def val(self, data):
        """store a value in node"""
        self.nodetype = C_DICT.id
        # clear old values
        for leaf in C_LEAVES:
            setattr(self, leaf.column, None)
        # test if we data is a leaf
        for leaf in C_LEAVES:
            if isinstance(data, leaf.types):
                # wipe children
                query = db.session.query(Node)
                query = query.filter(Node.parent == self)
                query.delete(synchronize_session='fetch')
                # remember type and store value
                self.nodetype = leaf.id
                setattr(self, leaf.column, data)
                return
        raise NotALeaf()

    def pickle(self, data):
        """recursively retrieve node data"""
        try:
            self.val = data
            return
        except NotALeaf:
            pass
        # not a leaf, a list or tuple?
        if isinstance(data, C_LIST.types):
            # make it a numbered dictionary
            self.nodetype = C_LIST.id
            data = dict(zip(range(len(data)), data))
        if isinstance(data, C_DICT.types):
            # wipe any child not being updated
            query = db.session.query(Node)
            query = query.filter(Node.parent == self)
            if data.keys():
                query = query.filter(sqlalchemy.not_(Node.label.in_(data.keys())))
            query.delete(synchronize_session='fetch')
            # store children
            for k, v in data.items():
                # fetch or create child and set it's value
                self.child(k, create=True).pickle(v)
            return
        raise Exception('unable to store type %s (%s)' % (type(data), data))

    def unpickle(self):
        """set node value recursively from a structure"""
        try:
            return self.val
        except NotALeaf:
            pass
        # structure
        result = {}
        for child in self.children:
            result[child.label] = child.unpickle()
        if self.nodetype == C_LIST.id:
            # flatten lists
            result = [result[i] for i in sorted(result)]
        return result

    def child(self, label, create=False):
        """fetch or chreate child by name"""
        query = db.session.query(Node)
        query = query.filter(Node.parent == self)
        query = query.filter(Node.label == label)
        result = query.first()
        if not result and create:
            result = Node(label, parent=self)
            db.session.add(result)
        return result

    @classmethod
    def root(cls):
        """return root node"""
        result = cls.query.filter_by(label='root', parent_id=None).first()
        return result

    @classmethod
    def fetch_by_path(cls, path, create=False):
        parent = cls.root()
        if not path:
            return parent
        for element in filter(None, path.split('/')):
            if parent.nodetype not in map(lambda x: x.id, C_BRANCHES):
                raise Exception("path %s contains leaf element %s" % (path, parent.label))
            node = cls.query.filter_by(label=element, parent=parent).first()
            if not node:
                if create:
                    node = Node(element, parent=parent)
                    db.session.add(node)
                else:
                    return None
            parent = node
        return parent

    @classmethod
    def get_by_path(cls, path):
        """start at the root node, walk the path and
        return the node matching"""
        return cls.fetch_by_path(path, create=False)

    @classmethod
    def create_path(cls, path, create=True):
        """create all intermediate notes up to path"""
        return cls.fetch_by_path(path, create=True)

    def __repr__(self):
        return '<Node %s: %s>' % (self.id, self.label)


db.create_all()
# create root Node
root = Node.query.filter_by(label='root', parent_id=None).first()
if not root:
    root = Node('root')
    db.session.add(root)
    db.session.commit()
