import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    JWT_SECRET_KEY = 'clave_secreta_super_segura'
    UPLOAD_FOLDER_CLASES = '/var/www/OkAprendeIngles/app/static/clases'
    UPLOAD_FOLDER_TAREAS = '/var/www/OkAprendeIngles/app/static/tareas'
    SECRET_KEY = 'clave_secreta_super_segura'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/gestion_ok'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
