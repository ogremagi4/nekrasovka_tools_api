from flask import Flask, request, current_app
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from flask_jwt_extended import JWTManager
from loguru import logger
import os

db = SQLAlchemy()
migrate=Migrate()
mail = Mail()

def add_and_commit(entries):
    if not isinstance(entries, list):
        db.session.add(entries)
    else:
        db.session.add_all(entries)
    db.session.commit()

def merge_and_commit(entries):
    try:
        logger.debug(f'Merging {len(entries)} entries')
        [db.session.merge(entry) for entry in entries]
        db.session.commit()
    except:
        db.session.rollback()
        raise

def delete_and_commit(entries):
    try:
        logger.debug(f'Deleting {len(entries)} entries')
        [db.session.delete(entry) for entry in entries]
        db.session.commit()
    except:
        db.session.rollback()
        raise
    
        

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt=JWTManager(app)
    mail.init_app(app)
    CORS(app)
    logger.start(
        os.path.join(app.config['LOG_PATH'], app.config['LOG_FILE']), 
        level = 'DEBUG', 
        format=app.config['LOG_FORMAT'], 
        rotation = app.config['LOG_ROTATION']
    )
    

    from app.users import bp as users_bp
    app.register_blueprint(users_bp)

    from app.eds import bp as eds_bp
    app.register_blueprint(eds_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    return app
