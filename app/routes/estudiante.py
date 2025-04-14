from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, current_app, send_from_directory, make_response

from app.services.serviciosEstudiante import ServiciosEstudiante
from app.services.serviciosSesion import ServiciosSesion
from app.services.serviciosActividad import ServiciosActividad
from app.models.estudiante import Estudiante
from app.config.extensiones import db
from app.services.serviciosAutenticacion import ServiciosAutenticacion, token_requerido

import os
import time
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

ALLOWED_EXTENSIONS_HOMEWORK = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp3', 'wav', 'ogg'}

def allowed_file_homework(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_HOMEWORK

estudiante_bp = Blueprint('estudiante_bp', __name__)



@estudiante_bp.route('/inicio', methods=['GET'])
@token_requerido
def vista_inicio(datos_usuario):
    id_estudiante = datos_usuario['id_usuario']
    estudiante = ServiciosEstudiante.obtener_por_id(id_estudiante)
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    actividades = ServiciosActividad.obtener_todos()
    if actividades:
        actividades_ordenadas = sorted(actividades, key=lambda x: x['fecha'], reverse=True)
    else:
        actividades_ordenadas = None

    return render_template('estudiante/inicio.html',
                           primer_nombre = primer_nombre, primer_apellido = primer_apellido,
                           actividades=actividades_ordenadas, estudiante = estudiante)

    
@estudiante_bp.route('/material', methods=['GET'])
@token_requerido
def vista_material(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('estudiante/material.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido)

# ------------------------------ SESIONES -----------------------------------------------

@estudiante_bp.route('/sesiones/disponiblesss', methods=['GET'])
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

    return redirect(url_for('estudiante_bp.vista_sesiones_disponibles_2'))


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

    #hoy = hoy - timedelta(days=1)

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

    tarea = ServiciosEstudiante.obtener_tarea_por_sesion(id)

    material_entregado = ServiciosEstudiante.obtener_material_por_sesion(id, id_estudiante)

    if sesion:
        return render_template("estudiante/ver_sesion.html", primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesion=sesion, detalle_sesion = datos_sesion, tarea=tarea, material_entregado=material_entregado)
    else:
        return redirect(url_for("estudiante_bp.vista_sesiones_inscritas"))



@estudiante_bp.route('/sesiones/tarea/<id>', methods=['POST'])
@token_requerido
def asignar_tarea(datos_usuario, id):

    id_estudiante = datos_usuario['id_usuario']
    

    referer = request.referrer

    if 'material' not in request.files:
        print("no existe el nombre material")
        
        if referer:
            return redirect(referer)
        else:
            # Si no hay referencia, rediriges a una página predeterminada
            return redirect(url_for('estudiante_bp.vista_sesiones_inscritas'))

    file = request.files['material']

    print(file)
    
    # Verificar si se seleccionó un archivo
    if file.filename == '':
        print("el filename es erroneo")
        if referer:
            return redirect(referer)
        else:
            # Si no hay referencia, rediriges a una página predeterminada
            return redirect(url_for('estudiante_bp.vista_sesiones_inscritas'))

    # Verificar si el archivo tiene una extensión permitida


    if file and allowed_file_homework(file.filename):
        # Renombrar el archivo usando el id de sesión y la fecha actual para evitar colisiones
        extension = os.path.splitext(file.filename)[1]

        session_id = str(id)  # Aquí se debe usar el ID de sesión o cualquier identificador único
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{session_id}_{id_estudiante}_{timestamp}{extension}"

        print('/*-'*50)
        print(filename)

        # Asegurarse de que el nombre del archivo sea seguro
        filename = secure_filename(filename)

        # Crear el directorio si no existe
        if not os.path.exists(current_app.config['UPLOAD_FOLDER_TAREAS']):
            os.makedirs(current_app.config['UPLOAD_FOLDER_TAREAS'])

        # Guardar la imagen temporalmente
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER_TAREAS'], filename)

        file.save(file_path)

        file_path = f'{filename}'
        asignado = ServiciosEstudiante.agregar_tarea(id, id_estudiante, file_path)



        if referer:
            return redirect(referer)
        else:
            # Si no hay referencia, rediriges a una página predeterminada
            return redirect(url_for('estudiante_bp.vista_sesiones_inscritas'))



    if referer:
        return redirect(referer)
    else:
        # Si no hay referencia, rediriges a una página predeterminada
        return redirect(url_for('estudiante_bp.vista_sesiones_inscritas'))


@estudiante_bp.route('/actividades/inscribirse/<int:id_actividad>', methods=['GET'])
@token_requerido
def inscribir_a_actividad(datos_usuario, id_actividad):
    id_estudiante = datos_usuario['id_usuario']
    
    # Aquí estamos llamando el método con los parámetros correctos
    resultado = ServiciosEstudiante.inscribir_a_actividad(id_estudiante, id_actividad)

    if resultado["status"] == "success":
        return redirect(url_for('estudiante_bp.vista_actividades_disponibles'))
    else:
        return jsonify(resultado), 500

@estudiante_bp.route('/actividades', methods=['GET'])
@token_requerido
def vista_actividades_disponibles(datos_usuario):
    id_estudiante = datos_usuario['id_usuario']
    estudiante = ServiciosEstudiante.obtener_por_id(id_estudiante)
    actividades = ServiciosActividad.obtener_todos()
    actividades_ordenadas = sorted(actividades, key=lambda x: x['fecha'], reverse=True)
    
    # Renderizas la plantilla correspondiente
    return render_template('estudiante/inicio.html', actividades=actividades_ordenadas, estudiante = estudiante)

@estudiante_bp.route('/reportes', methods=['GET'])
@token_requerido
def vista_reportes(datos_usuario):
    estudiante = ServiciosEstudiante.obtener_por_id(datos_usuario['id_usuario'])
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template(
        'estudiante/reportes.html',
        primer_nombre=primer_nombre,
        primer_apellido=primer_apellido, estudiante=estudiante
    )

@estudiante_bp.route('/usuarios/estudiantes/okcard/pdf/<id>', methods=['GET'])
@token_requerido
def generar_pdf_okcard_estudiante(datos_usuario, id):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosEstudiante.obtener_ok_card_pdf(nombre_usuario, id)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="okcard_estudiantes.pdf"'

    return response


# --------------------------------- NUEVAS RUTAS SESIONES --------------------

@estudiante_bp.route('/sesiones/disponibles', methods=['GET'])
@token_requerido
def vista_sesiones_disponibles_2(datos_usuario):

    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    id_estudiante = datos_usuario['id_usuario']

    sesiones_disponibles, sesiones_calendario, hora_actual, dia_actual, f_lunes, f_sabado = ServiciosEstudiante.obtener_sesiones_disponibles_estudiante_id_2(id_estudiante) # obtener_sesiones_disponibles_2(id_estudiante)

    lista_horas = ['07:30', '08:30', '09:30', '10:30', '11:30', '12:00','13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']
    fecha_lunes = datetime.strptime(f_lunes, "%Y-%m-%d")
    lista_fechas = []
    lista_fechas.append(fecha_lunes.strftime("%Y-%m-%d"))
    fecha_aa = fecha_lunes + timedelta(days=1)
    lista_fechas.append(fecha_aa.strftime("%Y-%m-%d"))
    fecha_aa = fecha_aa + timedelta(days=1)
    lista_fechas.append(fecha_aa.strftime("%Y-%m-%d"))
    fecha_aa = fecha_aa + timedelta(days=1)
    lista_fechas.append(fecha_aa.strftime("%Y-%m-%d"))
    fecha_aa = fecha_aa + timedelta(days=1)
    lista_fechas.append(fecha_aa.strftime("%Y-%m-%d"))
    fecha_aa = fecha_aa + timedelta(days=1)
    lista_fechas.append(fecha_aa.strftime("%Y-%m-%d"))

    #hora_actual = hora_actual, dia_actual = dia_actual, f_lunes = f_lunes, f_sabado = f_sabado
    return render_template('estudiante/sesiones_disponibles_2.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesiones = sesiones_disponibles, lista_horas = lista_horas, sesiones_calendario = sesiones_calendario, hora_actual = hora_actual, dia_actual = dia_actual, f_lunes = f_lunes, f_sabado = f_sabado, lista_fechas = lista_fechas)

@estudiante_bp.route('/sesiones/pasadas', methods = ['GET'])
@token_requerido
def vista_lista_sesiones_pasadas(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    id_estudiante = datos_usuario['id_usuario']

    sesiones_pasadas = ServiciosEstudiante.obtener_sesiones_pasadas_estudiante_id(id_estudiante)

    return render_template('estudiante/sesiones_pasadas.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesiones = sesiones_pasadas)

