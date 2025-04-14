from flask import Blueprint, request, jsonify

from flask import render_template, request, redirect, url_for, make_response, send_file

from app.services.serviciosAutenticacion import ServiciosAutenticacion, token_requerido
from app.services.serviciosUsuario import ServiciosUsuario

from datetime import datetime

def crear_blueprint(nombre_blueprint):
    bp = Blueprint(nombre_blueprint, __name__)

    #configuracion_bp = Blueprint('configuracion_bp', __name__)

    @bp.route('/ver', methods=['GET'])
    @token_requerido
    def vista_perfil_usuario(datos_usuario):
        nombres = datos_usuario['primer_nombre']
        apellidos = datos_usuario['primer_apellido']
        primer_nombre = nombres.split(' ')[0]
        primer_apellido = apellidos.split(' ')[0]
        id_usuario = datos_usuario['id_usuario']

        datos_usuario = ServiciosUsuario.obtener_usuario_por_id(id_usuario)

        return render_template('configuracion/ver_perfil.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, datos_usuario = datos_usuario)


    @bp.route('/configurar', methods=['GET'])
    @token_requerido
    def vista_configurar_usuario(datos_usuario):
        nombres = datos_usuario['primer_nombre']
        apellidos = datos_usuario['primer_apellido']
        primer_nombre = nombres.split(' ')[0]
        primer_apellido = apellidos.split(' ')[0]
        id_usuario = datos_usuario['id_usuario']

        datos_usuario = ServiciosUsuario.obtener_usuario_por_id(id_usuario)

        return render_template('configuracion/configurar_perfil.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, datos_usuario = datos_usuario)
    
    @bp.route('/configurar/datos', methods=['POST'])
    @token_requerido
    def guardar_datos(datos_usuario):
        datos = request.form
        nombres = datos['nombres']
        apellidos = datos['apellidos']
        telefono = datos['telefono']
        correo = datos['correo']

        id_usuario = datos_usuario['id_usuario']

        respuesta = ServiciosUsuario.configurar_usuario_por_id(id_usuario, nombres, apellidos, correo, telefono)

        return redirect(url_for(f'{nombre_blueprint}.vista_perfil_usuario'))


    return bp