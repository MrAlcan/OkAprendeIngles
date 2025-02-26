from flask import Blueprint, request, jsonify
from flask import render_template, request, redirect, url_for
from app.services.serviciosAdministrador import serviciosAdministrador

administrador_bp = Blueprint('administrador_bp', __name__)

@administrador_bp.route('/obtener_todos', methods=['GET'])
def obtener_administradores():
    administradores = serviciosAdministrador.obtener_todos()
    print(administradores)
    #return jsonify({'mensaje': administradores}), 201
    return render_template('administrador/tabla_muestra.html', datos = administradores)

@administrador_bp.route('/inicio', methods=['GET'])
def ver_plantilla():
    nombres = 'carlos'
    apellidos = 'yujra'
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('administrador/inicio.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido)

@administrador_bp.route('/usuarios/administradores', methods=['GET'])
def vista_lista_administradores():
    administradores = serviciosAdministrador.obtener_todos()
    nombres = 'carlos'
    apellidos = 'yujra'
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('administrador/administradores.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, administradores = administradores)