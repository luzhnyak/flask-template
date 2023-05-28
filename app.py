# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config


app = Flask(__name__)

app.secret_key = Config.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
# app.config['UPLOAD_FOLDER'] = upload_folder

db = SQLAlchemy(app)
