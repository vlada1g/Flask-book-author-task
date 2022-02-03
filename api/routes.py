from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid  
from werkzeug.security import generate_password_hash, check_password_hash
import os
import jwt
import datetime
from functools import wraps 
from api.models import User,Book
from api import app,db,redis_db

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
           
        if not token:
            return jsonify({'message' : 'Token is missing!'})
        if redis_db.get(token)==b'1':
            return jsonify({'message': 'User is loged out, please log in again'})
        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'})

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user.admin:
        return jsonify({'message':'Cannot perform that function!'})

    users=User.query.all() 
    output=[] 
    for user in users:
        user_data={}
        user_data['public_id']=user.public_id 
        user_data['name']=user.name   
        user_data['password']=user.password    
        user_data['admin'] = user.admin  
        user_data['authors'] = user.authors
        output.append(user_data)

    return jsonify({'users':output})

@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user,public_id):
    if not current_user.admin:
        return jsonify({'message':'Cannot perform that function!'})
    user= User.query.filter_by(public_id=public_id).first() 
    if not user:
        return jsonify({'message':'No user found!'})
    
    user_data={}
    user_data['public_id']=user.public_id 
    user_data['name']=user.name   
    user_data['password']=user.password    
    user_data['admin'] = user.admin  
    user_data['authors'] = user.authors
    
    return jsonify({'user': user_data})

@app.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    if not current_user.admin:
        return jsonify({'message':'Cannot perform that function!'})
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user= User.query.filter_by(name=data['name']).first()
    if user: 
        return jsonify({'message': 'Username already exist'})

    new_user= User(public_id=str(uuid.uuid4()),name=data['name'],password=hashed_password, admin=False, authors=False) 
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message' : 'New user has been created'})

@app.route('/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user,public_id):
    if not current_user.admin:
        return jsonify({'message':'Cannot perform that function!'})
    user= User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message':'No user found!'})

    user.authors=True 
    db.session.commit()
    return jsonify({'message': 'The user has been promoted!'})



@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user,public_id):
    if not current_user.admin:
        return jsonify({'message':'Cannot perform that function!'})
    user= User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message':'No user found!'})
    
    db.session.delete(user) 
    db.session.commit()

    return jsonify({'message': 'The user has been deleted!'})

@app.route('/login')
def login():
    auth=request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verigy',401, {'WWW-Autheticate': 'Basic realm="login requeired"'})

    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return jsonify({'message': "No user found"})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        redis_db.mset({str(token):0})
        redis_db.expire(str(token), 1800) # 30mins in sec expire time

        return jsonify({'token': token})

    
    return jsonify({'message': 'WRONG PASSWORD'})

@app.route('/main',methods=['GET'])
@token_required
def show_all_books(current_user):
    books= Book.query.all()
    output = []
    for book in books:
        book_data={}
        book_data['id']= book.id
        book_data['book_name']=book.book_name
        book_data['autor_name'] = book.autor_name
        output.append(book_data)
    return jsonify({'books':output})
    

@app.route('/author', methods=['GET'])
@token_required
def list_all_books_of_author(current_user):
    books= Book.query.filter_by(user_id=current_user.id).all()
    output = []
    for book in books:
        book_data={}
        book_data['id']= book.id
        book_data['book_name']=book.book_name
        book_data['autor_name'] = book.autor_name
        output.append(book_data)
    return jsonify({'books':output})


@app.route('/author/<book_id>', methods=['GET'])
@token_required
def list_one_book_of_author(current_user,book_id):
    book= Book.query.filter_by(id=book_id,user_id=current_user.id).first()
    
    if not book:
        return jsonify({'message': 'No book found'})
    book_data={}
    book_data['id']= book.id
    book_data['book_name']=book.book_name
    book_data['autor_name'] = book.autor_name
    
    return jsonify(book_data)

@app.route('/author', methods=['POST'])
@token_required
def add_book(current_user):
    data = request.get_json()

    new_book= Book(book_name=data['book_name'], autor_name=current_user.name, user_id= current_user.id)
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book has been added'})

@app.route('/author/<book_id>',methods=['PUT'])
@token_required
def edit_book(current_user,book_id):
    book= Book.query.filter_by(id=book_id, user_id=current_user.id).first()
    if not book:
        return jsonify({'message': 'No book found'})
    
    data = request.get_json()
    book.book_name=data['book_name']
    db.session.commit()
    return jsonify({'message': 'The book has been edited'})

@app.route('/author/<book_id>',methods=['DELETE'])
@token_required
def delete_book(current_user,book_id):
    book= Book.query.filter_by(id=book_id, user_id=current_user.id).first()
    if not book:
        return jsonify({'message': 'No book found'})
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'The book has been deleted'})

@app.route('/logout',methods=['GET'])
@token_required
def logout(current_user):
    if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
    if not token:
        return jsonify({'message' : 'Token is missing!'})

    redis_db.mset({str(token):1})

    return jsonify({'message': "User has been logout"})