from flask import Blueprint

bp = Blueprint('eds', __name__)

from app.eds import routes
