import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    BASEDIR=basedir
    POSTGRES_URL = os.environ.get("POSTGRES_URL")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PW = os.environ.get("POSTGRES_PW")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_URL}/{POSTGRES_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['admin@nekrasovka.ru']
    LANGUAGES = ['en', 'ru']
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    REDIS_HOST = 'localhost'
    REDIS_PASSWORD = ''
    REDIS_PORT = 6379
    REDIS_URL = 'redis://localhost:6379/0'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    LOG_PATH = "/tmp/"
    LOG_FILE = "nekrasovka_tools_api.log"
    LOG_FORMAT = "[<level>{level}</level> <green>{time:%Y-%m-%d %H:%M:%S.%f}</green>] [<fg #a4f9ff>module</fg #a4f9ff> <fg #ff9900>{file}</fg #ff9900>] [<red>def</red> <yellow>{function}</yellow>]:{line} | <blue>{message}</blue>"
    LOG_ROTATION = "25 MB"

    UPLOAD_FOLDER = f'{basedir}/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    KEYS_FOLDER = os.path.join(basedir, 'keys')#will store rsa keys for signing certs

    USER_IMAGES_FOLDER = os.path.join(basedir,'images')
    USER_FONTS_FOLDER  = os.path.join(basedir, 'fonts')

    STATIC_IMAGES_FOLDER = os.path.join(basedir,'static','images')
    STATIC_FONTS_FOLDER = os.path.join(basedir,'static','fonts')

    FRONTEND_DOMAIN = os.environ.get('FRONTEND_DOMAIN')

    CERT_TTL = os.environ.get('CERT_TTL')
    CERT_COUNTRY = os.environ.get("CERT_COUNTRY")
    CERT_STATE = os.environ.get("CERT_STATE")
    CERT_CITY = os.environ.get("CERT_CITY")
    CERT_ORGANIZATION = os.environ.get("CERT_ORGANIZATION")
    CERT_ORGANIZATIONAL_UNIT = os.environ.get("CERT_ORGANIZATIONAL_UNIT")
    


    




