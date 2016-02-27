from configdb.meta import app


@app.route('/')
def index():
    return 'Hello World'
