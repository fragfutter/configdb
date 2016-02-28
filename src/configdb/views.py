from configdb.meta import app
from configdb.meta import db
from configdb.schema import Node
from flask import request


def get_node(path, create=True):
    parent = Node.query.filter_by(label='root', parent_id=None).first()
    print(parent)
    for element in filter(None, path.split('/')):
        node = Node.query.filter_by(label=element, parent_id=parent.id).first()
        print(node)
        if not create and not node:
            print('no node and no create')
            return None
        if not node:
            print('creating node')
            node = Node(element, parent=parent)
            db.session.add(node)
            print('adding node')
            db.session.commit()  # possible race condition on multithread
            print('committed')
        parent = node
    return parent


@app.route('/')
def index():
    return 'Hello World'


@app.route('/configdb/v0/data/<path:path>', methods=['GET', 'PUT', 'DELETE'])
def v0_data(path):
    """get/put a single value"""
    # request.args.get('key', None)
    # request.headers.get('header', None)
    # TODO if it ends in / it is a list
    # TODO blobs are only returned on direct access
    # TODO determine return and set values from content-type header
    # POST = create, PUT = modify
    if request.method == 'POST' or request.method == 'PUT':
        n = get_node(path)
        # TODO format value according to Request headers
        n.val = request.data
        db.session.commit()
        return 'set value to %s' % request.data
    if request.method == 'GET':
        n = get_node(path)
        return 'val: %s' % n.val
    return path
