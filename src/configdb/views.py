from configdb.meta import app
from configdb.meta import db
from configdb.errors import HttpException, DecodeException, InvalidPath
from configdb.schema import Node
from configdb.formatter import Formatter
from flask import request, Response
from flask.views import MethodView
import sqlalchemy


mimes = {
    'application/json': 'json',
    'application/xml': 'xml',
    'text/plain': 'value',
    'text/html': 'value',
    'application/properties': 'properties',
    'application/yaml': 'yaml',
}


@app.route('/')
def index():
    return 'Hello World'


def get_response_format():
    """determine the reponse format the client requires.
    One of yaml, json, xml, value, properties ...
    """
    default = 'text/plain'
    keys = [default, ]
    keys.extend(mimes.keys())
    best = request.accept_mimetypes.best_match(
        keys,
        default=default)
    result = mimes[best]
    app.logger.debug('response format %s', result)
    return result


def decode_put():
    """transform put request data to internal data format"""
    data = request.data.decode('utf-8')  # check if this works in python2
    type_ = request.headers.get('content-type', default='text/plain')
    type_ = mimes.get(type_)
    if type_ is None:
        raise HttpException('unknown content-type')
    app.logger.info('content type is %s', type_)
    formatter = Formatter()
    if not hasattr(formatter, type_):
        raise HttpException('unable to handle content-type %s' % type_)
    try:
        setattr(formatter, type_, data)
    except DecodeException as e:
        raise HttpException('unable to decode: %s' % e)
    return formatter.data


class NodeAPIv1(MethodView):
    def get(self, path):
        formatter = Formatter()
        try:
            formatter.load(path)
        except InvalidPath as e:
            raise HttpException(e, code=404)
        return Response(formatter.json, mimetype='text/plain')

    def delete(self, path):
        return "delete"

    def put(self, path):
        data = decode_put()
        node = Node.create_path(path)
        self.save(node, data)
        db.session.commit()  # possible race condition on multithread
        return 'done'

    def save(self, node, data):
        """store nested dictionary of data on given node"""
        # TODO delete cascade
        # TODO move to formatter
        mapping = {
            'string': (str, ),
            'int': (int, ),
            'bool': (bool, ),
            'float': (float, ),
        }
        for db_type, typeset in mapping.items():
            if isinstance(data, typeset):
                query = db.session.query(Node)
                query = query.filter(Node.parent == node)
                query.delete(synchronize_session='fetch')
                node.type = db_type
                node.val = data
                return
        # list or set?
        if isinstance(data, (set, list, )):
            # make it a numbered dictionary
            data = dict(zip(range(len(data)), data))
            node.type = 'list'
        else:
            node.type = 'dict'
        node.val = None
        # ensure it is a dictionary
        assert isinstance(data, dict)
        for key, value in data.items():
            child = Node.query.filter_by(label=key, parent=node).first()
            if not child:
                child = Node(key, parent=node)
                db.session.add(child)
            self.save(child, value)
        # TODO delete any unknown children
        # delete from nodes where parent_id = node.id and label not in (...)
        query = db.session.query(Node)
        query = query.filter(Node.parent == node)
        query = query.filter(sqlalchemy.not_(Node.label.in_(data.keys())))
        query.delete(synchronize_session='fetch')


api_view = NodeAPIv1.as_view('api_v1')
app.add_url_rule(
    '/api/v1/',
    defaults={'path': None},
    view_func=api_view,
    methods=['GET', 'POST', 'PUT', 'DELETE'])
app.add_url_rule(
    '/api/v1/<path:path>',
    view_func=api_view,
    methods=['GET', 'POST', 'PUT', 'DELETE'])
