from flask import Flask, redirect, url_for, request

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

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return redirect(url_for('inicio_bp.vista_ingresar'))

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return redirect(url_for('inicio_bp.vista_ingresar'))
    
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return redirect(url_for('inicio_bp.vista_ingresar'))

    from app.routes.administrador import administrador_bp, token_requerido
    from app.routes.estudiante import estudiante_bp
    from app.routes.docente import docente_bp
    from app.routes.recepcionista import recepcionista_bp
    from app.routes.inicio import inicio_bp
    from app.routes.autenticacion import autenticar_bp

    '''@app.before_request
    def verificar_cookie():
        if not request.cookies.get('access_token'):
            return redirect(url_for('inicio_bp.vista_ingresar'))'''

    
    @app.errorhandler(404)
    def page_not_found(error):
        #rol = datos_usuario['rol']
        #direccion = str(rol) + '_bp.vista_inicio'
        #print(direccion)
        return redirect(url_for('inicio_bp.vista_ingresar'))
        return redirect(url_for('pagina_no_encontrada'))

    app.register_blueprint(administrador_bp, url_prefix='/administrador')
    app.register_blueprint(docente_bp, url_prefix='/docente')
    app.register_blueprint(estudiante_bp, url_prefix='/estudiante')
    app.register_blueprint(recepcionista_bp, url_prefix='/recepcionista')
    app.register_blueprint(inicio_bp, url_prefix='/inicio')
    app.register_blueprint(autenticar_bp, url_prefix='/autenticacion')




    return app