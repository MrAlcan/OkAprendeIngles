from flask import Blueprint, jsonify, render_template, request, redirect, url_for

from app.services.serviciosEstudiante import ServiciosEstudiante

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

# ------------------------------ SESIONES -----------------------------------------------

@estudiante_bp.route('/sesiones/disponibles', methods=['GET'])
@token_requerido
def vista_sesiones_disponibles(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    id_estudiante = datos_usuario['id_usuario']

    sesiones_disponibles, sesiones_calendario, hora_actual, dia_actual, f_lunes, f_sabado = ServiciosEstudiante.obtener_sesiones_disponibles(id_estudiante)

    lista_horas = ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00', '22:30']

    #hora_actual = hora_actual, dia_actual = dia_actual, f_lunes = f_lunes, f_sabado = f_sabado
    return render_template('estudiante/sesiones_disponibles.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesiones = sesiones_disponibles, lista_horas = lista_horas, sesiones_calendario = sesiones_calendario, hora_actual = hora_actual, dia_actual = dia_actual, f_lunes = f_lunes, f_sabado = f_sabado)


@estudiante_bp.route('/sesiones/inscribirse/<id>', methods = ['GET'])
@token_requerido
def inscribir_a_sesion(datos_usuario, id):
    id_estudiante = datos_usuario['id_usuario']

    inscripcion_sesion = ServiciosEstudiante.inscribir_a_sesion(id_estudiante, id)

    return redirect(url_for('estudiante_bp.vista_sesiones_disponibles'))


@estudiante_bp.route('/sesiones/inscritas', methods=['GET'])
@token_requerido
def vista_sesiones_inscritas(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]


    id_estudiante = datos_usuario['id_usuario']

    sesiones_disponibles, sesiones_calendario, hora_actual, dia_actual, f_lunes, f_sabado = ServiciosEstudiante.obtener_sesiones_inscritas(id_estudiante)

    lista_horas = ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00', '22:30']

    #hora_actual = hora_actual, dia_actual = dia_actual, f_lunes = f_lunes, f_sabado = f_sabado
    return render_template('estudiante/sesiones_inscritas.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesiones = sesiones_disponibles, lista_horas = lista_horas, sesiones_calendario = sesiones_calendario, hora_actual = hora_actual, dia_actual = dia_actual, f_lunes = f_lunes, f_sabado = f_sabado)
