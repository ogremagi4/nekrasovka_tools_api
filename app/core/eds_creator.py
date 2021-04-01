from genericpath import exists
from OpenSSL import crypto
import os
from app.users.models import User
from loguru import logger
from config import Config as app_config
import errno
from app.core.pdf_processor import PdfProcessor
import datetime
from dateutil.parser import parse
import time
from PIL import Image, ImageDraw, ImageFont
import textwrap

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: 
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

# def raw_cert(bytes_content):
#     return ('\n'.join(bytes_content.decode().split('\n')[1:-2])+'\n').encode()

def read_cert(filepath):
    cert = crypto.load_certificate(
    crypto.FILETYPE_PEM, 
    open(filepath).read()
    )
    return cert


class ElectronicDicgitalSignatureCreator:

    CERT_FILE = 'selfsigned.crt'
    PRIVATE_KEY_FILE = 'private.key'
    PUBLIC_KEY_FILE = 'public.key'
    PFX_FILE = 'selfsigned.pfx'
    
    def __init__(self, email, real_name) -> None:
        self.email = email#will use it for creating/checking created dirs for each creation method
        self.real_name = real_name
        self.stamp = os.path.join(app_config.USER_IMAGES_FOLDER, email, 'stamp.jpg')
        

    def _create_self_signed_cert(self, directory, email,common_name, cert_ttl, country='RU', state = 'Moscow', city='Moscow', organization='Nekrasovka', organizational_unit = 'Nekrasovka'):
        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 1024)
        # create a self-signed cert
        
        cert = crypto.X509()
        cert.get_subject().C = country
        cert.get_subject().ST = state
        cert.get_subject().L = city
        cert.get_subject().O = organization
        cert.get_subject().OU = organizational_unit
        cert.get_subject().CN = common_name
        cert.set_serial_number(int(time.time()))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(int(cert_ttl)*24*60*60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha1')
        open(self.cert_path, "wb+").write(
            crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        open(self.private_key_path, "wb+").write(
            crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
        open(self.public_key_path, "wb+").write(
            crypto.dump_publickey(crypto.FILETYPE_PEM, k))
        
        p12 = crypto.PKCS12()
        p12.set_privatekey(k)
        p12.set_certificate(cert)

        open(self.pfx_path, 'wb+').write(p12.export())

    def draw_user_stamp(self, example):#TODO
        cert = read_cert(self.cert_path)

        initial_lines = [
            'ДОКУМЕНТ ПОДПИСАН',
            'УСИЛЕННОЙ НЕКВАЛИФИЦИРОВАННОЙ',
            "ЭЛЕКТРОННОЙ ПОДПИСЬЮ"
        ]
        
        lines = [
            f'Сертификат: {cert.get_serial_number()}',
            f'Владелец: {self.real_name}',
            f"Действителен с {parse(cert.get_notBefore().decode()).strftime('%d.%m.%Y')} по {parse(cert.get_notAfter().decode()).strftime('%d.%m.%Y')}"
        ]

        image = Image.open(example)
        font_medium = ImageFont.truetype(os.path.join(app_config.STATIC_FONTS_FOLDER, 'Rubik-Medium.ttf'), size=20)
        font_regular = ImageFont.truetype(os.path.join(app_config.STATIC_FONTS_FOLDER, 'Rubik-Regular.ttf'), size=20)

        #draw initial lines
        draw = ImageDraw.Draw(image)


        W, H = 459,151#a rectangle near the logo 
        logo_pic_width = 133
        for cnt, line in enumerate(initial_lines):
            w,h = draw.textsize(line.encode('utf-8'))
            x = (W+logo_pic_width/3-w)/2
            y = (H/2-h)/2
            draw.text((x, y+cnt*h*3), line, font=font_medium, fill='black')
        
        #draw user part
        W, H = image.size
        for cnt, line in enumerate(lines):
            w,h = draw.textsize(line.encode('utf-8'))
            x = W/6
            y = (H-h)/2
            draw.text((x, y+cnt*h*3), line, font=font_regular, fill='black')

        image.save(self.stamp)

    def recreate_stamp_and_keys(self):
        self._create_self_signed_cert(self.user_keys_dir, self.email, self.real_name, cert_ttl=app_config.CERT_TTL, country=app_config.CERT_COUNTRY, state=app_config.CERT_STATE, city = app_config.CERT_CITY, organization=app_config.CERT_ORGANIZATION, organizational_unit=app_config.CERT_ORGANIZATIONAL_UNIT)
        self.draw_user_stamp(example = os.path.join(app_config.STATIC_IMAGES_FOLDER,'stamp.jpg'))


    def _check_files(self):#TODO
        user_keys_dir = os.path.join(app_config.KEYS_FOLDER, self.email)
        user_images_dir = os.path.join(app_config.USER_IMAGES_FOLDER, self.email)
        user_uploads_dir = os.path.join(app_config.UPLOAD_FOLDER, self.email)
        [mkdir_p(directory) for directory in [user_uploads_dir, user_keys_dir, user_images_dir]]

        self.pfx_path = os.path.join(user_keys_dir, self.PFX_FILE)
        self.cert_path = os.path.join(user_keys_dir, self.CERT_FILE)
        self.private_key_path = os.path.join(user_keys_dir, self.PRIVATE_KEY_FILE)
        self.public_key_path = os.path.join(user_keys_dir, self.PUBLIC_KEY_FILE)
        self.user_keys_dir = user_keys_dir

        if not all([os.path.exists(x) for x in [self.pfx_path, self.cert_path, self.private_key_path, self.public_key_path]]):
            logger.debug(f'Creating new crypto files for {self.email}')
            self.recreate_stamp_and_keys()

        elif os.path.exists(self.cert_path):
            cert = read_cert(self.cert_path)
            if cert.has_expired():#rectreate cert and stamp if expired
                logger.debug(f'{self.email} cert is expired, creating new one . . .')
                self.recreate_stamp_and_keys()

        if not os.path.exists(self.stamp):
            self.draw_user_stamp(example = os.path.join(app_config.STATIC_IMAGES_FOLDER,'stamp.jpg'))

    def sign_pdf(self, uploaded_filepath, signed_filepath):
        self._check_files()

        if os.path.exists(signed_filepath):
            logger.debug(f'Removing already existing signed file {signed_filepath}')
            os.remove(signed_filepath)

        #pdf stuff
        pdf_processor = PdfProcessor()
        #pdf_processor.certify_pdf(filepath, stamp_path, cert_field_name, pfx_path, '', certified_file)
        cert_field_name = 'NekrasovkaCertificationSig'
        pdf_processor.sign_pdf(uploaded_filepath, self.stamp, cert_field_name, self.pfx_path, '', signed_filepath)
        return signed_filepath