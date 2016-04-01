from configdb.meta import app
from configdb.meta import db
from configdb.errors import HttpException, DecodeException, InvalidPath
from configdb.formatter import Formatter
from flask import request, Response, render_template
from flask.views import MethodView


mimes = {
    'application/json': 'json',
    'application/xml': 'xml',
    'text/plain': 'value',
    'text/html': 'html',
    'application/properties': 'prop',
    'application/yaml': 'yaml',
}


@app.route('/')
def index():
    return 'Hello World'


def get_response_format():
    """determine the reponse format the client requires.
    One of yaml, json, xml, value, properties ...
    """
    # if a format is specified in the url, always use it
    try:
        return request.args['format']
    except KeyError:
        pass
    # otherwise determine it from accept mime types header
    default = 'text/html'
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
    result = request.headers.get('content-type', default='text/plain')
    result = mimes.get(result)
    if result is None:
        raise HttpException('unknown content-type')
    app.logger.info('content type is %s', result)
    return result


class NodeAPIv1(MethodView):
    def get(self, path):
        try:
            formatter = Formatter(path)
        except InvalidPath as e:
            raise HttpException(e, code=404)
        response_format = get_response_format()

        if response_format == 'html':
            # handle html in view
            if path is None:
                path = '/'
            if path and path[-1] != '/':
                path = path + '/'
            return render_template('node.html', node=formatter.node, path=path, params=request.args)
        # everything else must be handled by the formatter
        try:
            data = getattr(formatter, response_format)
        except AttributeError:
            raise HttpException('unknown format: %s' % response_format)
        return Response(data, mimetype='text/plain')

    def delete(self, path):
        return "delete"

    def put(self, path):
        put_format = decode_put()
        data = request.data.decode('utf-8')  # check if this works in python2
        if not hasattr(Formatter, put_format):
            raise HttpException('unable to handle content-type %s' % put_format)
        formatter = Formatter(path, create=True)
        try:
            setattr(formatter, put_format, data)
        except DecodeException as e:
            raise HttpException('unable to decode: %s' % e)
        db.session.commit()  # possible race condition on multithread
        return 'done'


api_view = NodeAPIv1.as_view('api_v1')
app.add_url_rule(
    '/api/v1/',
    defaults={'path': ''},
    view_func=api_view,
    methods=['GET', 'POST', 'PUT', 'DELETE'])
app.add_url_rule(
    '/api/v1/<path:path>',
    view_func=api_view,
    methods=['GET', 'POST', 'PUT', 'DELETE'])
