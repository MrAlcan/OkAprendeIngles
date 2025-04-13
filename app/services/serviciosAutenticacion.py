from app.models.usuario import Usuario
from app.config.extensiones import db, bcrypt
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal
from flask_jwt_extended import create_access_token, create_refresh_token, verify_jwt_in_request, get_jwt_identity
from functools import wraps
from flask import request, redirect, url_for, jsonify
import os
import jwt

def no_iniciar_sesion(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            #print(current_user)
            if str(current_user) == 'administrador':
                return redirect(url_for('administrador_bp.vista_inicio'))
            if str(current_user) == 'recepcionista':
                return redirect(url_for('recepcionista_bp.vista_inicio'))
            if str(current_user) == 'docente':
                return redirect(url_for('docente_bp.vista_inicio'))
            if str(current_user) == 'estudiante':
                return redirect(url_for('estudiante_bp.vista_inicio'))
        except:
            return f(*args, **kwargs)
    return wrapper

def token_requerido(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        token = request.cookies.get('access_token_cookie')
        #print(token)
        if not token:
            return redirect(url_for('inicio_bp.vista_ingresar'))

        cookie_cabecera = request.headers['Cookie'].split('; ')
        ruta = str(request.path)
        #print(f"ruta: {ruta}")
        rol_vista = ruta.split('/')[1]
        #print(f"rol_vista : {rol_vista}")
        #print(cookie_cabecera)
        ac_co_tok = cookie_cabecera[0].split('=')
        csrf_tok = cookie_cabecera[1].split('=')
        cuerpo_token = {
            f'{ac_co_tok[0]}': f'{ac_co_tok[1]}',
            f'{csrf_tok[0]}': f'{csrf_tok[1]}'
        }
        #print(cuerpo_token['access_token_cookie'])
        
        try:
            data = jwt.decode(cuerpo_token['access_token_cookie'], os.environ.get('SECRET_KEY'), algorithms=['HS256'])
            if str(data['rol']) != str(rol_vista):
                direccion = str(data['rol']) + '_bp.vista_inicio'
                return redirect(url_for(direccion))
            #print(data['sub'])
            #user_id = data['sub']['id_usuario']
            #datos_usuario = data['sub']
            datos_usuario = {
                "id_usuario": data['id_usuario'],
                "nombre_usuario": data['nombre_usuario'],
                "rol": data['rol'],
                "primer_nombre": data['primer_nombre'],
                "primer_apellido": data['primer_apellido'],
                "nombres": data['nombres'],
                "apellidos": data['apellidos']
            }
        except jwt.ExpiredSignatureError:
            #return jsonify({'message': 'Token expired'}), 401
            return redirect(url_for('inicio_bp.vista_ingresar'))
        except jwt.InvalidTokenError:
            #return jsonify({'message': 'Invalid token'}), 401
            return redirect(url_for('inicio_bp.vista_ingresar'))
        
        return f(datos_usuario, *args, **kwargs)
    
    return wrapper

class ServiciosAutenticacion():

    def autenticar_nombre_usuario(nombre_usuario):
        usuario = Usuario.query.filter_by(nombre_usuario = nombre_usuario).first()
        if usuario:
            return True, usuario.id_usuario
        else:
            return False, 'Nombre de Usuario no Encontrado'
    
    def autenticar_contrasena(id_usuario, contrasena):
        usuario = Usuario.query.get(id_usuario)
        respuesta = bcrypt.check_password_hash(usuario.contrasena_hash, contrasena)

        if respuesta:
            return True, usuario.rol
        else:
            return False, 'Contraseña Erronea'
    
    def generar_token(id_usuario):
        usuario = Usuario.query.get(id_usuario)
        if usuario:
            primer_nombre = str(usuario.nombres).split(' ')[0]
            primer_apellido = str(usuario.apellidos).split(' ')[0]
            cuerpo_identidad = {'id_usuario': usuario.id_usuario,
                                 'nombre_usuario': usuario.nombre_usuario,
                                 'rol': usuario.rol,
                                 'primer_nombre': primer_nombre,
                                 'primer_apellido': primer_apellido,
                                 'nombres': usuario.nombres,
                                 'apellidos': usuario.apellidos}
            #token = create_access_token(identity=cuerpo_identidad) #FUNCIONABA AHROA NO 26/02/2025
            token = create_access_token(identity=str(usuario.rol), additional_claims=cuerpo_identidad) # NUEVO INTENTO
            
            return token
            
        else:
            print("Usuario no encontrado")
            return False
