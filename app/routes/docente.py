from flask import Blueprint, jsonify, render_template, request, redirect, url_for, send_from_directory, current_app

from app.services.serviciosAdministrador import serviciosAdministrador
from app.services.serviciosRecepcionista import ServiciosRecepcionista

from app.services.serviciosUsuario import ServiciosUsuario
from app.services.serviciosSesion import ServiciosSesion
from app.services.serviciosEstudiante import ServiciosEstudiante
from datetime import datetime



from app.services.serviciosAutenticacion import ServiciosAutenticacion, token_requerido
from app.services.serviciosDocentes import ServiciosDocente

import os
import time
from werkzeug.utils import secure_filename
from PIL import Image

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS_HOMEWORK = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp3', 'wav', 'ogg'}

def allowed_file_homework(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_HOMEWORK

# Función para verificar si la extensión de la imagen es válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Función para cambiar el tamaño de la imagen antes de guardarla
def resize_image(image, max_size=(800, 800)):
    image.thumbnail(max_size)
    return image

# Función para convertir a formato JPG
def convert_to_jpg(image):
    if image.format != 'JPEG':
        img = image.convert('RGB')
        return img
    return image


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


@docente_bp.route('/sesiones', methods=['GET'])
@token_requerido
def vista_lista_sesiones(datos_usuario):

    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]


    id_docente = datos_usuario['id_usuario']

    sesiones = ServiciosDocente.obtener_sesiones_docente(id_docente)


    return render_template('docente/lista_sesiones.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesiones=sesiones)

@docente_bp.route('/sesiones/ver/<id>', methods=['GET'])
@token_requerido
def vista_sesion_por_id(datos_usuario, id):

    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]


    id_docente = datos_usuario['id_usuario']

    sesion = ServiciosDocente.obtener_sesion_por_id(id_docente, id)

    

    if not sesion:
        return redirect(url_for("docente_bp.vista_lista_sesiones"))
    
    tareas = ServiciosDocente.obtener_tarea_por_sesion(id)
    
    detalle_sesion = ServiciosDocente.obtener_detalles_sesion(id)
    print(detalle_sesion)

    detalle_tarea = ServiciosDocente.obtener_detalle_tareas_por_sesion(id)
    

    return render_template("docente/ver_sesion.html", primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesion=sesion, detalle_sesion=detalle_sesion, tarea=tareas, detalle_tareas=detalle_tarea)

@docente_bp.route('/sesiones/link/<id>', methods=['POST'])
@token_requerido
def asignar_link(datos_usuario, id):
    
    link_reunion = request.form['link']

    print(link_reunion)

    asignado = ServiciosDocente.asignar_link(id, link_reunion)

    referer = request.referrer


    if referer:
        return redirect(referer)
    else:
        # Si no hay referencia, rediriges a una página predeterminada
        return redirect(url_for('docente_bp.vista_lista_sesiones'))


@docente_bp.route('/sesiones/asistencia/<id>', methods=['POST'])
@token_requerido
def llenado_asistencias(datos_usuario, id):

    estudiantes_asistieron = request.form.getlist('asistencias[]')

    estudiantes_data = []

    estudiantes_asistencia = {}
    estudiantes_notas = {}

    # Recoger la nota y recomendación solo de los estudiantes que asistieron
    for estudiante_id_str in estudiantes_asistieron:
        # Obtener la nota y la recomendación para este estudiante

        estudiantes_asistencia[estudiante_id_str] = 'Asistio'
        
        nota = request.form.get(f'nota_{estudiante_id_str}')
        recomendacion = request.form.get(f'recomendacion_{estudiante_id_str}')
        estudiantes_notas[estudiante_id_str] = [nota, recomendacion]
        
        # Guardar la información en una lista o diccionario para procesarla
        estudiantes_data.append({
            'id_estudiante': estudiante_id_str,
            'nota': nota,
            'recomendacion': recomendacion
        })

    #print('/*-'*50)
    print("datos_esto")
    print(estudiantes_data)

    llenado = ServiciosDocente.asignar_asistencias_notas(estudiantes_data, id)

    referer = request.referrer

    if 'image' not in request.files:
        if referer:
            return redirect(referer)
        else:
            # Si no hay referencia, rediriges a una página predeterminada
            return redirect(url_for('docente_bp.vista_lista_sesiones'))

    file = request.files['image']
    
    # Verificar si se seleccionó un archivo
    if file.filename == '':
        if referer:
            return redirect(referer)
        else:
            # Si no hay referencia, rediriges a una página predeterminada
            return redirect(url_for('docente_bp.vista_lista_sesiones'))

    # Verificar si el archivo tiene una extensión permitida
    if file and allowed_file(file.filename):
        # Renombrar el archivo usando el id de sesión y la fecha actual para evitar colisiones
        session_id = str(id)  # Aquí se debe usar el ID de sesión o cualquier identificador único
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{session_id}_{timestamp}.jpg"

        # Asegurarse de que el nombre del archivo sea seguro
        filename = secure_filename(filename)

        # Crear el directorio si no existe
        if not os.path.exists(current_app.config['UPLOAD_FOLDER_CLASES']):
            os.makedirs(current_app.config['UPLOAD_FOLDER_CLASES'])

        # Guardar la imagen temporalmente
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER_CLASES'], filename)

        # Abrir la imagen con Pillow
        image = Image.open(file)

        # Redimensionar y convertir la imagen
        image = resize_image(image)
        image = convert_to_jpg(image)

        # Guardar la imagen final en el directorio
        image.save(file_path, 'JPEG')

        # Devolver la URL de la imagen guardada
        imagen_url = f'clases/{filename}'

        sub_img = ServiciosDocente.subir_imagen(id, imagen_url)



        if referer:
            return redirect(referer)
        else:
            # Si no hay referencia, rediriges a una página predeterminada
            return redirect(url_for('docente_bp.vista_lista_sesiones'))

    if referer:
        return redirect(referer)
    else:
        # Si no hay referencia, rediriges a una página predeterminada
        return redirect(url_for('docente_bp.vista_lista_sesiones'))


    if referer:
        return redirect(referer)
    else:
        # Si no hay referencia, rediriges a una página predeterminada
        return redirect(url_for('docente_bp.vista_lista_sesiones'))




@docente_bp.route('/uploads/<path:filename>')
def download_file(filename):
    print(current_app.config['UPLOAD_FOLDER_CLASES'])
    print(filename)
    return send_from_directory('/cargados/clases',filename)



@docente_bp.route('/sesiones/tarea/<id>', methods=['POST'])
@token_requerido
def asignar_tarea(datos_usuario, id):

    id_docente = datos_usuario['id_usuario']
    descripcion_tarea = request.form['descripcion']

    print(descripcion_tarea)

    referer = request.referrer

    if 'material' not in request.files:
        print("no existe el nombre material")
        asignado = ServiciosDocente.asignar_tarea(id, descripcion_tarea, None)
        if referer:
            return redirect(referer)
        else:
            # Si no hay referencia, rediriges a una página predeterminada
            return redirect(url_for('docente_bp.vista_lista_sesiones'))

    file = request.files['material']

    print(file)
    
    # Verificar si se seleccionó un archivo
    if file.filename == '':
        print("el filename es erroneo")
        asignado = ServiciosDocente.asignar_tarea(id, descripcion_tarea, None)
        if referer:
            return redirect(referer)
        else:
            # Si no hay referencia, rediriges a una página predeterminada
            return redirect(url_for('docente_bp.vista_lista_sesiones'))

    # Verificar si el archivo tiene una extensión permitida


    if file and allowed_file_homework(file.filename):
        # Renombrar el archivo usando el id de sesión y la fecha actual para evitar colisiones
        extension = os.path.splitext(file.filename)[1]

        session_id = str(id)  # Aquí se debe usar el ID de sesión o cualquier identificador único
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{session_id}_{id_docente}_{timestamp}{extension}"

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
        asignado = ServiciosDocente.asignar_tarea(id, descripcion_tarea, file_path)



        if referer:
            return redirect(referer)
        else:
            # Si no hay referencia, rediriges a una página predeterminada
            return redirect(url_for('docente_bp.vista_lista_sesiones'))


    asignado = ServiciosDocente.asignar_tarea(id, descripcion_tarea, None)
    if referer:
        return redirect(referer)
    else:
        # Si no hay referencia, rediriges a una página predeterminada
        return redirect(url_for('docente_bp.vista_lista_sesiones'))



    asignado = ServiciosDocente.asignar_tarea(id, descripcion_tarea)

    referer = request.referrer


    if referer:
        return redirect(referer)
    else:
        # Si no hay referencia, rediriges a una página predeterminada
        return redirect(url_for('docente_bp.vista_lista_sesiones'))
    

@docente_bp.route('/download/<filename>')
def download_file_h(filename):
    # Validar que el archivo existe
    #file_path = os.path.join('app','static','tareas', filename)
    file_path = os.path.join('var', 'www', 'OkAprendeIngles', 'app', 'static', 'tareas', filename)
    #filename = str(filename).split('/')[1]
    print(filename)
    print(file_path)
    if os.path.exists(file_path):
        print("existes")
        #file_path = os.path.join(os.getcwd(),'app','static','tareas')
        file_path = os.path.join('var', 'www', 'OkAprendeIngles','app','static','tareas')
        # Usamos send_from_directory para enviar el archivo
        return send_from_directory(file_path, path=filename, as_attachment=False)

    return jsonify({"error": "File not found"}), 404



@docente_bp.route('/sesiones/semana', methods=['GET'])
@token_requerido
def vista_lista_sesiones_semana(datos_usuario):

    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]


    id_docente = datos_usuario['id_usuario']

    lista_horarios, lista_sesiones, dia_actual, fecha_actual, f_lunes, f_sabado = ServiciosDocente.obtener_sesiones_semana_docente_por_id(id_docente)

    lista_horas = ['07:30', '08:30', '09:30', '10:30', '11:30', '12:00','13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00']
    

    return render_template("docente/sesiones_semana.html", primer_nombre = primer_nombre, primer_apellido = primer_apellido, lista_horarios=lista_horarios, lista_sesiones=lista_sesiones, dia_actual=dia_actual, fecha_actual=fecha_actual, lista_horas=lista_horas, f_sabado=f_sabado, f_lunes=f_lunes)

@docente_bp.route('/material', methods=['GET'])
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

    return render_template('docente/material.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, enlaces_archivos=enlaces_archivos, enlaces_audios=enlaces_audios)
