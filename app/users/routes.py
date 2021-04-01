from flask import Flask, request, jsonify, make_response
from app.users.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.users import bp
from flask_jwt_extended import jwt_required, get_jwt_identity
from inflection import underscore
from app import db
import uuid
import sqlalchemy

@bp.route('/users', methods=['GET'])
@jwt_required
def get_all_users():

    users = User.query.all()

    output = [{k:v for k,v in i.to_dict().items() if k in ['name','password_hash']} for i in users]

    return jsonify(output)

@bp.route('/users/<email>', methods=['GET'])
@jwt_required
def get_one_user(email):

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user_data = {k:v for k,v in user.to_dict().items() if k in ['email','password_hash']}
    
    return jsonify(user_data), 200

@bp.route('/users', methods=['POST'])
def create_user():
    body = ({underscore(k): v for k,
             v in request.get_json().items() if not k in ['limit']})
    hashed_password = generate_password_hash(body['password'], method='sha256')
    new_user = User(id=str(uuid.uuid4()), **{k:v for k,v in body.items() if k in User.__table__.columns}, password_hash=hashed_password)
    try:
        db.session.add(new_user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        user_message=f'User {new_user.email} already registered'
        return jsonify({'msg':user_message}), 409

    message=f'User {body["email"]} successfully registered'
    return jsonify({'msg':message}), 200