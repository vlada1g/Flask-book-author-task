from api import db 
from datetime import datetime        


class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    public_id=db.Column(db.String(50),unique=True) 
    name= db.Column(db.String(50), unique= True) 
    password = db.Column(db.String(50)) 
    admin = db.Column(db.Boolean)
    authors = db.Column(db.Boolean)

# class Todo(db.Model):
#     id = db.Column(db.Integer, primary_key=True)  
#     text = db.Column(db.String(50))
#     complete = db.Column(db.Boolean)
#     user_id=db.Column(db.Integer)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    autor_name=db.Column(db.String(50)) 
    book_name = db.Column(db.String(50))
    user_id=db.Column(db.Integer)