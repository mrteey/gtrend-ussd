
'''
gtrend
--------------
'''
#Basic Flask Requirements
from flask import Flask, request, render_template, url_for, redirect, session, flash

from gtrend.model import db

import os

from flask_migrate import Migrate

#instance of app
app = Flask(__name__, instance_relative_config=False)


#cookie generator
app.secret_key = os.urandom(24)

#configs
app.config.from_object(os.environ.get('config'))

db.init_app(app)

migrate = Migrate(app, db)

#TODO: 
# Modify this import to reflect your desired blueprint
# Check blue print folder for more
from gtrend.api.routes import api

# TODO: 
# You can register more blueprints here
app.register_blueprint(api)