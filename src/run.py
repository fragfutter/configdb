#!/usr/bin/python
import logging
from configdb import app

log_werkzeug = logging.getLogger('werkzeug')
log_werkzeug.setLevel(logging.WARNING)
app.run(host='0.0.0.0')
