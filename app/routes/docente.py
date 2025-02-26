from flask import Blueprint, jsonify, render_template, request, redirect, url_for

from app.services.serviciosAutenticacion import ServiciosAutenticacion, token_requerido

docente_bp = Blueprint('docente_bp', __name__)


@docente_bp.route('/inicio', methods=['GET'])
@token_requerido
def vista_inicio(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('docente/inicio.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido)
