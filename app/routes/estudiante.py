from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash

from app.services.serviciosEstudiante import ServiciosEstudiante
from app.services.serviciosSesion import ServiciosSesion

from app.services.serviciosAutenticacion import ServiciosAutenticacion, token_requerido

from datetime import datetime, timedelta

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

    lista_horas = ['07:30', '08:30', '09:30', '10:30', '11:30', '12:00','13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']

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

    print(sesiones_calendario)
    print(sesiones_disponibles)

    lista_horas = ['07:30', '08:30', '09:30', '10:30', '11:30', '12:00','13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']

    #hora_actual = hora_actual, dia_actual = dia_actual, f_lunes = f_lunes, f_sabado = f_sabado

    numero_dia = 1
    if dia_actual == 'Martes':
        numero_dia = 2
    elif dia_actual == 'Miercoles':
        numero_dia = 3
    elif dia_actual == 'Jueves':
        numero_dia = 4
    elif dia_actual == 'Viernes':
        numero_dia = 5
    elif dia_actual == 'Sabado':
        numero_dia = 6
    elif dia_actual == 'Domingo':
        numero_dia = 7
            
    return render_template('estudiante/sesiones_inscritas.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesiones = sesiones_disponibles, lista_horas = lista_horas, sesiones_calendario = sesiones_calendario, hora_actual = hora_actual, dia_actual = dia_actual, f_lunes = f_lunes, f_sabado = f_sabado, numero_dia = numero_dia)

@estudiante_bp.route('/sesiones/cancelar/<id>', methods=['POST'])
@token_requerido
def cancelar_inscripcion_sesion(datos_usuario, id):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    id_estudiante = datos_usuario['id_usuario']

    datos = request.form

    hoy = datetime.now()
    hoy = hoy + timedelta(minutes=30)

    hoy = hoy - timedelta(days=1)

    fecha_sesion = str(datos['fecha'])
    hora_sesion = str(datos['hora'])
    print("/*-*/"*100)
    print(hora_sesion)
    justificacion = str(datos['justificacion'])

    fecha_hora_sesion = datetime.strptime(fecha_sesion +" "+hora_sesion, "%Y-%m-%d %H:%M:%S")

    if hoy<fecha_hora_sesion:
        cancelado = ServiciosEstudiante.cancelar_registro(id_estudiante, id, justificacion)
        return redirect(url_for('estudiante_bp.vista_sesiones_inscritas'))
    else:
        #sesiones_disponibles, sesiones_calendario, hora_actual, dia_actual, f_lunes, f_sabado = ServiciosEstudiante.obtener_sesiones_inscritas(id_estudiante)

        #lista_horas = ['07:30', '08:30', '09:30', '10:30', '11:30', '12:00','13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']

        mensaje = "No se pudo cancelar la inscripción a la sesión por límite de tiempo"

        #hora_actual = hora_actual, dia_actual = dia_actual, f_lunes = f_lunes, f_sabado = f_sabado
        flash(mensaje, "error")
        return redirect(url_for('estudiante_bp.vista_sesiones_inscritas'))
        #return render_template('estudiante/sesiones_inscritas.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesiones = sesiones_disponibles, lista_horas = lista_horas, sesiones_calendario = sesiones_calendario, hora_actual = hora_actual, dia_actual = dia_actual, f_lunes = f_lunes, f_sabado = f_sabado, mensaje = mensaje)


@estudiante_bp.route('/sesiones/ver/<id>', methods=['GET'])
@token_requerido
def vista_sesion_id(datos_usuario, id):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    id_estudiante = datos_usuario['id_usuario']

    sesion, datos_sesion = ServiciosEstudiante.obtener_datos_sesion(id, id_estudiante)

    if sesion:
        return render_template("estudiante/ver_sesion.html", primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesion=sesion, detalle_sesion = datos_sesion)
    else:
        return redirect(url_for("estudiante_bp.vista_sesiones_inscritas"))




