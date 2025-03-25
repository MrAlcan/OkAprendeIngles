from flask import Blueprint, request, jsonify
from flask import render_template, request, redirect, url_for
from app.services.serviciosAdministrador import serviciosAdministrador
from app.services.serviciosRecepcionista import ServiciosRecepcionista
from app.services.serviciosDocentes import ServiciosDocente
from app.services.serviciosAutenticacion import ServiciosAutenticacion, token_requerido
from app.services.serviciosUsuario import ServiciosUsuario
from app.services.serviciosSesion import ServiciosSesion
from app.services.serviciosEstudiante import ServiciosEstudiante
from datetime import datetime

docente_bp = Blueprint('docente_bp', __name__)

@docente_bp.route('/obtener_todos', methods=['GET'])
@token_requerido
def obtener_administradores(datos_usuario):
    administradores = serviciosAdministrador.obtener_todos()
    #print(administradores)
    #return jsonify({'mensaje': administradores}), 201
    return render_template('administrador/tabla_muestra.html', datos = administradores)

@docente_bp.route('/inicio', methods=['GET'])
@token_requerido
def vista_inicio(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('docente/inicio.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido)

@docente_bp.route('/usuarios', methods=['GET'])
@token_requerido
def vista_lista_usuarios(datos_usuario):
    usuarios = ServiciosUsuario.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('docente/usuarios.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, usuarios = usuarios)

@docente_bp.route('/usuarios/habilitar/<id>', methods=['GET'])
@token_requerido
def habilitar_usuario(datos_usuario, id):
    usuario = ServiciosUsuario.activar_usuario(id)
    return redirect(url_for('docente_bp.vista_lista_usuarios'))

@docente_bp.route('/usuarios/deshabilitar/<id>', methods=['GET'])
@token_requerido
def deshabilitar_usuario(datos_usuario, id):
    usuario = ServiciosUsuario.desactivar_usuario(id)
    return redirect(url_for('docente_bp.vista_lista_usuarios'))

@docente_bp.route('/usuarios/recepcionistas', methods=['GET'])
@token_requerido
def vista_lista_docentes(datos_usuario):
    docentes = ServiciosDocente.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('administrador/docentes.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes, administrador=datos_usuario, horarios=horarios)
