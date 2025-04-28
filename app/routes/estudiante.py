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

    enlaces_carpetas = []
    enlaces_audios = ['',
        '18ErSHq7NQ5iY3JKkMattdRVPOIk9_t5J',
        '1-Kd7OjuhMK2qpBP-R3qRpDojIdjn7TuL',
        '1CJ39anVvfu2s4v_570d8m19Yi96AGKbr',
        '1xRafWQ-9xUNiEcJWcLvbzk9vbhm7cd7q',
        '1E0L28ACdAqmZLV67C_lImUFZ20bv5b3_',
        '1fBZA0bpTFtqRhhvwcaah_OiQH-QTQLRp',
        '108bqRriFcPMUG9KdR4OkTQRfUztD4fni',
        '19klQ214jdsWQtq2anJgjSu5tVoPehpeq',
        '1_9X8j7m8vcbfmX-2x7PgWp_eDzy6SFqN',
        '1UMrOIJyy7Wcb5Lb-M8h7T8ig4RVG9SMz',
        '1OMy3eMh5Tmdaz3Hp8RE4RGeT7FHfwq9S',
        '1CsDjYksMj8Pvy5KrQcakv7j5ue3rzWRG',
        '1aV-3VtrXyMhwubSOrK9KcOtyBhoUOGk_',
        '1wFBsTXuGnN5EEbRtYqDfgHqNQX_a94zi',
        '168xEJf8SjV5VPrXpOxBtT9C2JS1hJzgD',
        '17W5v0yFyBFK2TfA1UNSUJC9SWH0J2ZsY',
        '1wL-T0JCD9QgNmrS6RpXC79NS8-_PdyPC',
        '10Wlh5ZfzFKPS92HiJMjYfXtT2lDukiu0',
        '1UCgG9p_x7Cla8DDLVAScq5ZZid4miBSr',
        '1UYcqNHpv71fQf2ZzAraWuaNHPBPPMrtu',
        '1ldfFc51B_LTp1mm1vRiMsraFnjIgeNGv',
        '1_DYhivjo_hfZBVU3NLCNEFgW4fWj96fS',
        '1JY1Egfwh4JkfOZo6jt7d82jDu6t-z9PD',
        '1vrpMZuRCH6Wh3Fml12HEkGX2aTbWMe96',
        '1ihlettF4NcdG8pWyqi2MQMlg6-hB4XJM',
        '1tPZltYpEWtx6-hbazl587Gn9ox0YR5rQ',
        '1QR1MaKXl_QaOLefI3-MAkcEZFZJp5sKq',
        '19Yk-vgyfX31_3a9-tCxr_PE28m9Ncqtt',
        '11z69rwxOkuZZ0NdVl-oyCcS0hYYFUMnk',
        '1Y0y2wohjEANNAk2lW4e3-70p29nLztkX',
        '1mgjOeLg8dwe_AlusTxCtVwASpPMk4X8U',
        '16ylTw2b7qtK9p8bzxenl_80qITG-qNpc',
        '1yzSMinVuCI1jq9VtUunO9VkRWvXml9yG',
        '1flMBV3MHf0kIK8tljL5PNcQVRJqNYcRA',
        '1l-06pbqyLJ4J5ik3vuD2aFnnkQOeclaO',
        '1qgQRuW-k7PqsPR5o6f4IyXWX7x0wH92N',
        '1VD3BhjIF5a4OC5Cmf3RzFmQg-PjpiaMN',
        '1mQ_AnvQaKHzMzd73wdVT-LMoAMYpIx2s',
        '1DXK-5z6l5QRNlkRcSQQRd-sYdJNBuiWz',
        '1F1fxp-4FVOwcFnAqpkK-z4ZCDG45q46i',
        '1SKwiIKAGBtSQz3-w_mix1dr2TfJWnlJT',
        '1HS-TBYAIIV1rx0iunPnKh1OXqGvxrkBI',
        '1KPPZGetg9f4NkVRh7CWokPaQtrWZljbu',
        '1d-6_o9MP2Uk_WzIdUcWDkclMDC5N3Vfn',
        '1x-s2MByVO4MOZTMWVmKiNH0Vs071ynCU',
        '1ak2OaNu0ZfJbWGMd5w7b6Y89-cRgfoPZ',
        '1_lY8zvbSl9MPa7DUaq3SB68O3dgm8dRb',
        '10gwSHQNJB9uYhYMbOjY8sAh-fqOOwWU8',
        '12WZH9gtLbrXjCjU-FvC0QQ0aw2Lzp8ep',
        '1A5PZ1ZQiU2NPQ04NzCD8d7NYvHQhGEAh'
    ]
    enlaces_archivos = ['',
        '1yMyhQ_fGWpYtDsbojn7bnoYjFe5zy7-J',
        '1jdmo4ZU7rqB3I5Sh8ssz0FkPDs5_7U8R',
        '1aPuFY5GJjRsmox0okuj5wXGExWi8ruR9',
        '1-eB7mjtBIfFezeBtayOW4VTQtfATEKef',
        '1lRMCXsgQO1NahV9Lc9rM6VadAGhp8nPC',
        '1imoIURJYIx2VH-qkztZGKk5yyxuzczOb',
        '1mfX9gYMJY8CnXCDGiVnYjCdNLPelBoDj',
        '1Eqsm3MEW4ji3QQLAOJWUtONVIhVmdt22',
        '1m52SfxJExBNFqSkemAHfrztDi7Goob2v',
        '1M1rr711lYbVykn4YpjXZL2kPkrs9Dw9I',
        '13ZvKG08_PYCpdUxEzBoO6AOo_9gK8tsl',
        '1OHc3dN8O8noMmtsq_C7maFZ920IrM5d8',
        '1m-qEhUOg4lCxoi_4rqyPbm8X0YPxqnK0',
        '1mVYdzhguvHpkP1BCyCQIRqz4ymSb65Rc',
        '1Iug92kTGmhYB0EaCls_-2iaZlIVxLUNN',
        '1_-CvLXJgiZNuHVXtgAVghBoONSSot_yZ',
        '1JVoYfjnGBaSfyBJFBYB1LiGhqXm1gPfd',
        '1VVbJu3KInajl4tlZjuDKRQPAiGsq8zpj',
        '1IsIIzBdH2lunIKzD79rCzKAQAhFdC8DP',
        '1xGZPTm44qQGhVB_2QBFePzHatkZhgkKB',
        '1EOcSEJNNk2a2suHDa6MrPhbg198F9bOP',
        '1oUmhrH7HMWo_RY1fjBWKyNFibplQDmSh',
        '1ZNQS8FuMaWryqINhtLpow7Xl1uNpapd-',
        '1Z7pOOKLpvP7yIKNEXC1y5QElD3xh2r1S',
        '1qnKUujypsdYNIWEk85xYB-iQRbDhFb5q',
        '14UmvNRc0ps8MhKLjbRXydxyvoUCuPACR',
        '1YiGqVMET5iLbBGv4q-dIuOC0AQ7RWzBD',
        '1bR4-okOMneA6zyjHPJcW7zNZpPEIPmqK',
        '1XljQ52WJ08CYBP-umKDMgI7V9tUy0hxP',
        '1g5UMNfwmbRl1qXccWU2vxXpHRSdtKHMS',
        '1eDGXXC6gb5aYh-dKNiLJVWE8WKYpiXUT',
        '1s_r6B3b1w-TifYJoByFcPRfjjSbt3b7G',
        '1q-iNdi_WixlaEgnU7nMh2P1q6780VNMq',
        '1YQKhoAePtWtf0o7lh5w8yx_f3oQaYNJz',
        '1VixP5BUeorLdYHTbMJgW04SWi4868L60',
        '1cZ16wIIPXAcNsnlxvYs7scs5gEs01bg-',
        '1dEB7Pc2W0U_vHUSydjBzjhLGPj7kXmEi',
        '1sd6qeyXdlNmvQuGDDZ52KDZVVMfEgDn5',
        '1AkYpk0EI--vfOav4v0jZEGmpOzx5p9uR',
        '1nOssIGURRvMWJT80QzWbPxbEGM7UlIVM',
        '1mSp2R-VDPSBcEHYxUIzoPcNYCxNjBt6q',
        '1jSKMQVUNbUorLFyRwPIohaeVj0V1h8u0',
        '1tg2ETGVQeLPbMtHB3LgDxwerEBVxiWJZ',
        '1vnMIESc4cHahVkiMSnyOARwTnaFHPIca',
        '1rnzz1q9x9PnMomwn041nVVMOAj54ty7a',
        '1KaMrw-Pf493Ia-WW7iihi49nW02GCtk4',
        '12CVlP7F5WvGCVnmdp-xuucgoYAlO_RZg',
        '1BopDvqrg40k9iW-VSDlTWnI7pfRtIaK2',
        '1DuxFYP1Kvcz1fye76oh-ddsYFdnjgq-o',
        '1SYHZqgZh5wy7RV993urdMzBB2bdFsu6v'
    ]

    return render_template('estudiante/material.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, enlaces_archivos=enlaces_archivos, enlaces_audios=enlaces_audios)

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



@estudiante_bp.route('/perfil', methods=['GET'])
@token_requerido
def vista_perfil(datos_usuario):
    estudiante = ServiciosEstudiante.obtener_por_id(datos_usuario['id_usuario'])
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    return render_template(
        'estudiante/perfil.html',
        primer_nombre=primer_nombre,
        primer_apellido=primer_apellido, estudiante=estudiante
    )