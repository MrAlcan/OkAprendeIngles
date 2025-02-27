from flask import Blueprint, request, jsonify
from flask import render_template, request, redirect, url_for
from app.services.serviciosAdministrador import serviciosAdministrador
from app.services.serviciosRecepcionista import ServiciosRecepcionista
from app.services.serviciosDocentes import ServiciosDocente
from app.services.serviciosAutenticacion import ServiciosAutenticacion, token_requerido

administrador_bp = Blueprint('administrador_bp', __name__)

@administrador_bp.route('/obtener_todos', methods=['GET'])
@token_requerido
def obtener_administradores(datos_usuario):
    administradores = serviciosAdministrador.obtener_todos()
    print(administradores)
    #return jsonify({'mensaje': administradores}), 201
    return render_template('administrador/tabla_muestra.html', datos = administradores)

@administrador_bp.route('/inicio', methods=['GET'])
@token_requerido
def vista_inicio(datos_usuario):
    nombres = datos_usuario['primer_nombre']
    apellidos = datos_usuario['primer_apellido']
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('administrador/inicio.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido)

@administrador_bp.route('/usuarios/administradores', methods=['GET'])
@token_requerido
def vista_lista_administradores(datos_usuario):
    administradores = serviciosAdministrador.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('administrador/administradores.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, administradores = administradores)

@administrador_bp.route('/crear/administrador', methods=['POST'])
@token_requerido
def crear_administrador(datos_usuario):
    datos = request.form
    nuevo_administrador = serviciosAdministrador.crear(datos['nombre_usuario'], datos['contrasena'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['telefono_personal'])
    if nuevo_administrador:
        return redirect(url_for('administrador_bp.vista_lista_administradores'))
    else:
        return jsonify({'codigo': 400})
    
@administrador_bp.route('/usuarios/recepcionistas', methods=['GET'])
@token_requerido
def vista_lista_recepcionistas(datos_usuario):
    recepcionistas = ServiciosRecepcionista.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('administrador/recepcionistas.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, recepcionistas = recepcionistas)

@administrador_bp.route('/crear/recepcionista', methods=['POST'])
@token_requerido
def crear_recepcionista(datos_usuario):
    datos = request.form
    nuevo_administrador = ServiciosRecepcionista.crear(datos['nombre_usuario'], datos['contrasena'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['telefono_personal'])
    if nuevo_administrador:
        return redirect(url_for('administrador_bp.vista_lista_recepcionistas'))
    else:
        return jsonify({'codigo': 400})

@administrador_bp.route('/usuarios/docentes', methods=['GET'])
@token_requerido
def vista_lista_docentes(datos_usuario):
    docentes = ServiciosDocente.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('administrador/docentes.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes)

@administrador_bp.route('/crear/docente', methods=['POST'])
@token_requerido
def crear_docente(datos_usuario):
    datos = request.form
    nuevo_administrador = ServiciosRecepcionista.crear(datos['nombre_usuario'], datos['contrasena'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['telefono_personal'])
    if nuevo_administrador:
        return redirect(url_for('administrador_bp.vista_lista_docentes'))
    else:
        return jsonify({'codigo': 400})