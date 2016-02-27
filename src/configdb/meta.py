from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_pyfile('base.cfg')
if 'CONFIGDB_SETTINGS' in os.environ:
    app.config.from_envvar('CONFIGDB_SETTINGS')

db = SQLAlchemy(app)
