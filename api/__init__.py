from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import redis

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SECRET_KEY']= "thisissecret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
redis_db=redis.Redis()
db=SQLAlchemy(app) 

from api import routes,models