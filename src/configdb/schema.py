from configdb.meta import db


class Node(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('node.id'))
    parent = db.relationship(
        'Node',
        backref=db.backref('children', lazy='dynamic')
    )
    type_ = db.Column(db.String)

    def __repr__(self):
        return '<Node %s>' % self.id

db.create_all()

print('configdb.schema')
