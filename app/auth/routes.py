from app import create_app, merge_and_commit
from flask import Flask, json, request, jsonify, make_response, current_app, render_template
import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, jwt_required, decode_token
from app.users.models import User
from app.auth import bp
from flask_mail import Message
from threading import Thread
from loguru import logger
import traceback
from app import mail
from urllib.parse import urlencode
from inflection import underscore



def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except:
            logger.exception(traceback.format_exc())

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(create_app(), msg)).start()


@bp.route('/auth/reset', methods = ['POST'])
def reset_password():
    body = ({underscore(k):v for k,v in request.get_json().items()})
    logger.debug(body)
    reset_token = body.get('reset_token')
    password = body.get('password')

    if not reset_token or not password:
        raise Exception('No reset token or password')

    email = decode_token(reset_token)['identity']
    user = User.query.filter(User.email == email).first_or_404()
    user.password_hash = generate_password_hash(password)
    merge_and_commit([user])
    return jsonify({'msg':f'Changed password for {email}'})


@bp.route('/auth/forgot', methods=['POST'])
def forgot_password():
    body = ({underscore(k):v for k,v in request.get_json().items()})
    email = body.get('email')
    user = User.query.filter(User.email == email).first_or_404()
    reset_token = create_access_token(str(user.email), expires_delta=datetime.timedelta(hours=24))
    url = current_app.config['FRONTEND_DOMAIN'] + 'auth/reset-password?'
    user_msg_template = "Hi. Use this link to reset your password"
    encoded_url = url+ urlencode({'reset_token':reset_token})
    send_email('Nekrasovka tools password reset',
                              sender='support@nekrasovka.ru',#TODO change to fine sender
                              recipients=[user.email],
                              text_body=f"{user_msg_template} : {encoded_url}",
                              html_body=f"{user_msg_template} : {encoded_url}")
    return jsonify({'msg':f"Sent with reset link to {email}"})

@bp.route('/login',methods=['POST'])
def login():
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        return make_response('User or password missing', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = User.query.filter_by(email=auth.username).first()

    if not user:
        return make_response('User not registered', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(user.password_hash, auth.password):
        token = create_access_token(identity=str(user.email), expires_delta= datetime.timedelta(days=30))
        return jsonify({
            'token' : token, 
            'refresh_token': create_refresh_token(identity=str(user.email)), 
            'msg': f'Welcome {auth.username}'}), 200
    return jsonify({'error':True, 'msg':'Could not verify'}), 401  


@bp.route('/token/refresh', methods=['POST'])
#@jwt_required
def refresh():
    current_user = get_jwt_identity()
    return jsonify({'token' : create_access_token(identity=current_user),'msg':'Access token was refreshed'}), 200