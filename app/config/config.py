import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:

    JWT_SECRET_KEY = os.environ.get('SECRET_KEY')
    UPLOAD_FOLDER_CLASES = 'app/static/clases'
    UPLOAD_FOLDER_TAREAS = 'app/static/tareas'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = ['cookies'] # posiblemente no se use
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)