from flask import Flask

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.config.config import Config
from app.config.database import iniciar_datos
from app.config.extensiones import db, bcrypt, jwt



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    
    
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    from app.routes.administrador import administrador_bp
    from app.routes.inicio import inicio_bp

    app.register_blueprint(administrador_bp, url_prefix='/administrador')
    app.register_blueprint(inicio_bp, url_prefix='/inicio')




    return app