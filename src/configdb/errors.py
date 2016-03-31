from configdb.meta import app
from flask import make_response


class DecodeException(Exception):
    pass


class InvalidPath(Exception):
    pass


class NotALeaf(Exception):
    """trying to access a branch node in leaf context"""
    pass


class HttpException(Exception):
    def __init__(self, message, code=400, **kwargs):
        self.message = str(message)
        self.status_code = code
        self.data = kwargs

    def to_dict(self):
        result = {'message': self.message}
        result.update(self.data)
        return result


@app.errorhandler(HttpException)
def handle_invalid_usage(error):
    response = make_response(error.message)
    response.status_code = error.status_code
    return response
