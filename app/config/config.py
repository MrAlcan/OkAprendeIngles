import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    JWT_SECRET_KEY = 'clave_secreta_super_segura'
    UPLOAD_FOLDER_CLASES = '/var/www/okaprendeingles/app/static/clases'
    UPLOAD_FOLDER_TAREAS = '/var/www/okaprendeingles/app/static/tareas'
    SECRET_KEY = 'clave_secreta_super_segura'
    SQLALCHEMY_DATABASE_URI = 'mysql://usuario_ok:usuario_ok_seguro@localhost/gestion_ok'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
