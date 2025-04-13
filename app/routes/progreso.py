from flask import render_template
from app.models.estudiante import Estudiante
from app.config.extensiones import db
from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from app.services.serviciosActividad import ServiciosActividad
from app.services.serviciosAutenticacion import token_requerido

progreso_bp = Blueprint('progreso_bp', __name__)

# ------------------------- RUTAS ACTIVIDAD ----------------------------

@progreso_bp.route('/progreso', methods=['GET'])
@token_requerido
def obtener_progreso(id_estudiante):
    progresos = serviciosEstudiante.obtener_progreso()
    return jsonify(progresos)

@progreso_bp.route('/progreso/<int:id_estudiante>')
def progreso(id_estudiante):
    estudiante = Estudiante.query.get(id_estudiante)
    if not estudiante:
        return "Estudiante no encontrado", 404
    return render_template('estudiante/progreso.html', estudiante=estudiante)

