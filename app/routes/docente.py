from flask import Blueprint, jsonify, render_template, request, redirect, url_for, send_from_directory, current_app

from app.services.serviciosAutenticacion import ServiciosAutenticacion, token_requerido
from app.services.serviciosDocentes import ServiciosDocente

import os
import time
from werkzeug.utils import secure_filename
from PIL import Image

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    
    detalle_sesion = ServiciosDocente.obtener_detalles_sesion(id)
    print(detalle_sesion)
    

    return render_template("docente/ver_sesion.html", primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesion=sesion, detalle_sesion=detalle_sesion)

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

    print('/*-'*50)
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