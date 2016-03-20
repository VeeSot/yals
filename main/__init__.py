from os.path import abspath, dirname

import pymongo

from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mongoengine import MongoEngine
from flask.templating import Environment

app = Flask(__name__)

# DB settings
app.config["MONGODB_SETTINGS"] = {
    'DB': "yals"}
app.config["SECRET_KEY"] = "secret_key"
db = MongoEngine(app)
# connection through pymogo for low-level request
connection = pymongo.MongoClient()
connection_db = connection.yals

# Add Bootstrap
Bootstrap(app)
# Local static files
ROOT_PATH = dirname(dirname(abspath(__file__)))
STATIC_ROOT = ROOT_PATH + '/static'
assets = Environment(app)
assets.app.root_path = ROOT_PATH
assets.directory = STATIC_ROOT

def register_blueprints(app):
    # Prevents circular imports
    from entities.views import entities
    app.register_blueprint(entities)


register_blueprints(app)

if __name__ == '__main__':
    app.run()
