from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from api.models import User,Book
from api import app,db     
import uuid  
from werkzeug.security import generate_password_hash

db.create_all()
hashed_password = generate_password_hash("12345", method='sha256')
new_user= User(public_id=str(uuid.uuid4()),name="Admin",password=hashed_password, admin=True, authors=True) 
db.session.add(new_user)
db.session.commit()