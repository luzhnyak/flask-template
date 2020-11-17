# -*- coding: utf-8 -*-

from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_sqlalchemy import SQLAlchemy
from app import *
from models import *

@app.route("/")
def index():	
	return render_template('index.html', TITLE="Start Flask")