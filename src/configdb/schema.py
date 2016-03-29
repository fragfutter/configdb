from configdb.meta import db

T_BOOL = 1
T_INT = 2
T_FLOAT = 3
T_STRING = 4
T_BLOB = 5

t_map = {
    T_BOOL: 'bool',
    T_INT: 'int',
    T_FLOAT: 'float',
    T_STRING: 'string',
    T_BLOB: 'blob',
}


class Node(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('node.id'))
    children = db.relationship(
        'Node',
        backref=db.backref('parent', remote_side=[id]),
    )
    type = db.Column(db.String)
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
        self.type = 'string'

    @property
    def val(self):
        if self.type in ('bool', 'int', 'float', 'string'):
            return getattr(self, self.type + 'val')
        else:
            return None

    @val.setter
    def val(self, val):
        # clear old values
        self.boolval = None
        self.intval = None
        self.floatval = None
        self.stringval = None
        self.blobval = None
        if self.type in ('bool', 'int', 'float', 'string'):
            setattr(self, self.type + 'val', val)

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
            if parent.type not in ('dict', 'list'):
                raise Exception("path %s contains leaf element %s" % (path, parent.label))
            node = cls.query.filter_by(label=element, parent=parent).first()
            if not node:
                if create:
                    node = Node(element, parent=parent)
                    node.type = 'dict'
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
    root.type = 'dict'
    db.session.add(root)
    db.session.commit()
