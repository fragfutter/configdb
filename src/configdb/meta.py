from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_pyfile('base.cfg')
if 'CONFIGDB_SETTINGS' in os.environ:
    app.config.from_envvar('CONFIGDB_SETTINGS')

db = SQLAlchemy(app)


@db.event.listens_for(db.engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    print("activating foreign keys")
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
