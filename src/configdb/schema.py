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
        print('val is %s' % self.stringval)
        return getattr(self, self.type + 'val')

    @val.setter
    def val(self, val):
        setattr(self, self.type + 'val', val)

    def __repr__(self):
        return '<Node %s: %s>' % (self.id, self.label)


db.create_all()
# create root Node
root = Node.query.filter_by(label='root', parent_id=None).first()
if not root:
    root = Node('root')
    db.session.add(root)
    db.session.commit()

print('configdb.schema')
