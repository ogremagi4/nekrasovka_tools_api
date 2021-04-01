from flask.helpers import send_from_directory
from app.users.models import User
from flask import Flask, json, request, jsonify, make_response, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_raw_jwt
from werkzeug.utils import secure_filename
from app import create_app, merge_and_commit
from app.eds import bp
from inflection import underscore
from loguru import logger
import os
import app
import errno
from config import Config
from app.core.eds_creator import mkdir_p
from app.core.eds_creator import ElectronicDicgitalSignatureCreator
from time import sleep
import zipfile
import io



ALLOWED_EXTENSIONS = set(['pdf'])
#'doc', 'docx',])#TODO make .doc(x) support after some examples are provided

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/eds', methods = ['GET'])
def get_eds():
    pass

@bp.route('/eds', methods = ['POST'])
@jwt_required
def post_eds():
    """
    Read the input file, create a signature, return a zip with signed file and a signature
    """
    f = request.files['file']
    if not f:
        return jsonify({'msg':'No file was provided'})

    elif not allowed_file(f.filename):
        return jsonify({'msg':f'File not in allowed extensions. Allowed: {" ".join(ALLOWED_EXTENSIONS)}.'})

    email = get_jwt_identity()
    real_name = User.query.filter(User.email == email).first().real_name
    creator = ElectronicDicgitalSignatureCreator(email, real_name)

    uploaded_filename, signed_filename = [f'{x}_{f.filename}'.replace(' ','_') for x in ['uploaded','signed']]
    uploaded_filepath = os.path.join(Config.UPLOAD_FOLDER, email, uploaded_filename)
    signed_filepath = os.path.join(Config.UPLOAD_FOLDER, email, signed_filename)
    mkdir_p(os.path.join(Config.UPLOAD_FOLDER, email))
    f.save(uploaded_filepath)
    
    if f.filename.endswith('.pdf'):
        pdf_filepath = creator.sign_pdf(uploaded_filepath, signed_filepath)#create signed pdf
        return send_file(pdf_filepath, attachment_filename=os.path.basename(pdf_filepath), as_attachment=True, cache_timeout=0, mimetype='application/pdf')
        

