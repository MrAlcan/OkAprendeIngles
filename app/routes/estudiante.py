from flask import Blueprint, jsonify, render_template, request, redirect, url_for

from app.services.serviciosAutenticacion import ServiciosAutenticacion, token_requerido

estudiante_bp = Blueprint('estudiante_bp', __name__)


@estudiante_bp.route('/inicio', methods=['GET'])
@token_requerido
def vista_inicio(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('estudiante/inicio.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido)
