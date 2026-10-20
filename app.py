# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config
from context import inject_constants

app = Flask(__name__)

app.secret_key = Config.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{
    Config.APP_FOLDER}/db/data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"

app.context_processor(inject_constants)

db = SQLAlchemy(app)
