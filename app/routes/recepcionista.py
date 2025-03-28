from flask import Blueprint, request, jsonify
from flask import render_template, request, redirect, url_for
from app.services.serviciosAdministrador import serviciosAdministrador
from app.services.serviciosRecepcionista import ServiciosRecepcionista
from app.services.serviciosDocentes import ServiciosDocente
from app.services.serviciosAutenticacion import ServiciosAutenticacion, token_requerido
from app.services.serviciosUsuario import ServiciosUsuario
from app.services.serviciosSesion import ServiciosSesion
from app.services.serviciosActividad import ServiciosActividad
from app.services.serviciosEstudiante import ServiciosEstudiante
from datetime import datetime

recepcionista_bp = Blueprint('recepcionista_bp', __name__)

@recepcionista_bp.route('/obtener_todos', methods=['GET'])
@token_requerido
def obtener_administradores(datos_usuario):
    administradores = serviciosAdministrador.obtener_todos()
    #print(administradores)
    #return jsonify({'mensaje': administradores}), 201
    return render_template('administrador/tabla_muestra.html', datos = administradores)

@recepcionista_bp.route('/inicio', methods=['GET'])
@token_requerido
def vista_inicio(datos_usuario):
    nombres = datos_usuario['primer_nombre']
    apellidos = datos_usuario['primer_apellido']
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('recepcionista/inicio.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido)

@recepcionista_bp.route('/usuarios', methods=['GET'])
@token_requerido
def vista_lista_usuarios(datos_usuario):
    usuarios = ServiciosUsuario.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('recepcionista/usuarios.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, usuarios = usuarios)




@recepcionista_bp.route('/usuarios/habilitar/<id>', methods=['GET'])
@token_requerido
def habilitar_usuario(datos_usuario, id):
    usuario = ServiciosUsuario.activar_usuario(id)
    return redirect(url_for('recepcionista_bp.vista_lista_usuarios'))

@recepcionista_bp.route('/usuarios/deshabilitar/<id>', methods=['GET'])
@token_requerido
def deshabilitar_usuario(datos_usuario, id):
    usuario = ServiciosUsuario.desactivar_usuario(id)
    return redirect(url_for('recepcionista_bp.vista_lista_usuarios'))


@recepcionista_bp.route('/usuarios/recepcionistas', methods=['GET'])
@token_requerido
def vista_lista_recepcionistas(datos_usuario):
    recepcionistas = ServiciosRecepcionista.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('recepcionista/recepcionistas.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, recepcionistas = recepcionistas)

@recepcionista_bp.route('/crear/recepcionista', methods=['POST'])
@token_requerido
def crear_recepcionista(datos_usuario):
    datos = request.form
    nuevo_administrador = ServiciosRecepcionista.crear(datos['nombre_usuario'], datos['contrasena'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['telefono_personal'])
    if nuevo_administrador:
        return redirect(url_for('recepcionista_bp.vista_lista_recepcionistas'))
    else:
        return jsonify({'codigo': 400})

@recepcionista_bp.route('/usuarios/docentes', methods=['GET'])
@token_requerido
def vista_lista_docentes(datos_usuario):
    docentes = ServiciosDocente.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('recepcionista/docentes.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes, horarios=horarios)

@recepcionista_bp.route('/crear/docente', methods=['POST'])
@token_requerido
def crear_docente(datos_usuario):
    datos = request.form
    dias = []
    horas_inicio = []
    horas_final = []

    for clave, valor in datos.items():
        if clave.startswith('dia_'):
            id_dia = int(clave.split('_')[1])
            dias.append((id_dia, valor))
        elif clave.startswith('h_inicio_'):
            id_h_inicio = int(clave.split('_')[2])
            horas_inicio.append((id_h_inicio, valor))
        elif clave.startswith('h_final_'):
            id_h_final = int(clave.split('_')[2])
            horas_final.append((id_h_final, valor))
    
    dias_ordenados = sorted(dias, key=lambda x: x[0])
    lista_dias = [valor for dia, valor in dias_ordenados]

    horas_inicio_ordenados = sorted(horas_inicio, key=lambda x: x[0])
    lista_horas_inicio = [valor for hora, valor in horas_inicio_ordenados]

    horas_final_ordenados = sorted(horas_final, key=lambda x: x[0])
    lista_horas_final = [valor for hora, valor in horas_final_ordenados]

    nuevo_docente = ServiciosDocente.crear(datos['nombre_usuario'], datos['contrasena'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['asignacion_tutor'], lista_dias, lista_horas_inicio, lista_horas_final, datos['color'])

    #nuevo_administrador = ServiciosRecepcionista.crear(datos['nombre_usuario'], datos['contrasena'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['telefono_personal'])
    #if nuevo_administrador:
    #    return redirect(url_for('administrador_bp.vista_lista_docentes'))
    #else:
    #    return jsonify({'codigo': 400})
    return redirect(url_for('recepcionista_bp.vista_lista_docentes'))

@recepcionista_bp.route('/editar/docente/<id>', methods=['POST'])
@token_requerido
def editar_docente(datos_usuario, id):
    datos = request.form

    ids_horarios_eliminados = datos['input_horarios_eliminados'].split('_')[0:-1]
    '''print('*/'*100)
    print(datos)
    print(datos['input_horarios_eliminados'].split('_')[0:-1])'''
    
    dias = []
    horas_inicio = []
    horas_final = []

    dias_existentes = []
    horas_inicio_existentes = []
    horas_final_existentes = []
    ids_horarios_existentes = []

    for clave, valor in datos.items():
        if clave.startswith('dia_'):
            id_dia = int(clave.split('_')[1])
            dias.append((id_dia, valor))
        elif clave.startswith('h_inicio_'):
            id_h_inicio = int(clave.split('_')[2])
            horas_inicio.append((id_h_inicio, valor))
        elif clave.startswith('h_final_'):
            id_h_final = int(clave.split('_')[2])
            horas_final.append((id_h_final, valor))
        elif clave.startswith('o_dia_'):
            id_dia = int(clave.split('_')[2])
            dias_existentes.append((id_dia, valor))
            ids_horarios_existentes.append(id_dia)
        elif clave.startswith('o_h_inicio_'):
            id_h_inicio = int(clave.split('_')[3])
            horas_inicio_existentes.append((id_h_inicio, valor))
        elif clave.startswith('o_h_final_'):
            id_h_final = int(clave.split('_')[3])
            horas_final_existentes.append((id_h_final, valor))
    
    dias_ordenados = sorted(dias, key=lambda x: x[0])
    lista_dias = [valor for dia, valor in dias_ordenados]

    horas_inicio_ordenados = sorted(horas_inicio, key=lambda x: x[0])
    lista_horas_inicio = [valor for hora, valor in horas_inicio_ordenados]

    horas_final_ordenados = sorted(horas_final, key=lambda x: x[0])
    lista_horas_final = [valor for hora, valor in horas_final_ordenados]

    dias_ordenados_existentes = sorted(dias_existentes, key=lambda x: x[0])
    lista_dias_existentes = [valor for dia, valor in dias_ordenados_existentes]

    horas_inicio_ordenados_existentes = sorted(horas_inicio_existentes, key=lambda x: x[0])
    lista_horas_inicio_existentes = [valor for hora, valor in horas_inicio_ordenados_existentes]

    horas_final_ordenados_existentes = sorted(horas_final_existentes, key=lambda x: x[0])
    lista_horas_final_existentes = [valor for hora, valor in horas_final_ordenados_existentes]

    lista_ids_existentes_ordenados = sorted(ids_horarios_existentes)
    '''print('*/-'*100)
    print(lista_ids_existentes_ordenados)
    print(dias_ordenados_existentes)
    print(horas_inicio_ordenados_existentes)
    print(horas_final_ordenados_existentes)'''

    docente = ServiciosDocente.actualizar(id, datos['nombre_usuario'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['asignacion_tutor'], lista_dias, lista_horas_inicio, lista_horas_final, ids_horarios_eliminados, lista_ids_existentes_ordenados, lista_dias_existentes, lista_horas_inicio_existentes, lista_horas_final_existentes, datos['color'])

    #nuevo_docente = ServiciosDocente.crear(datos['nombre_usuario'], datos['contrasena'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['asignacion_tutor'], lista_dias, lista_horas_inicio, lista_horas_final)

    
    
    return redirect(url_for('recepcionista_bp.vista_lista_docentes'))

@recepcionista_bp.route('/docente/eliminar/<id>', methods=['GET'])
@token_requerido
def eliminar_docente(datos_usuario, id):
    docente = ServiciosDocente.eliminar(id)
    return redirect(url_for('recepcionista_bp.vista_lista_docentes'))

@recepcionista_bp.route('/editar/recepcionista/<id>', methods=['POST'])
@token_requerido
def editar_recepcionista(datos_usuario, id):
    datos = request.form
    recepcionista = ServiciosRecepcionista.actualizar(id, datos['nombre_usuario'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'])

    return redirect(url_for('recepcionista_bp.vista_lista_recepcionistas'))

@recepcionista_bp.route('/recepcionista/eliminar/<id>', methods=['GET'])
@token_requerido
def eliminar_recepcionista(datos_usuario, id):
    recepcionista = ServiciosRecepcionista.eliminar(id)
    return redirect(url_for('recepcionista_bp.vista_lista_recepcionistas'))



# ----------------------- GESTION SESIONES ----------------------------------

@recepcionista_bp.route('/sesiones', methods=['GET'])
@token_requerido
def vista_lista_sesiones(datos_usuario):
    docentes = ServiciosDocente.obtener_todos()
    print('/*-'*100)
    print(docentes)
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    sesiones = ServiciosSesion.obtener_todos()
    return render_template('recepcionista/sesiones.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes, sesiones = sesiones)

@recepcionista_bp.route('/sesiones/crear', methods=['POST'])
@token_requerido
def crear_sesion(datos_usuario):
    id_usuario = str(datos_usuario['id_usuario'])

    datos = request.form

    sesion = ServiciosSesion.crear(datos['fecha'], datos['hora'], datos['docente'], datos['seccion'], datos['nivel'], datos['cupos'])

    return redirect(url_for('recepcionista_bp.vista_lista_sesiones'))

@recepcionista_bp.route('/sesiones/editar/<id>', methods=['POST'])
@token_requerido
def editar_sesion(datos_usuario, id):
    datos = request.form

    sesion = ServiciosSesion.actualizar(id, datos['fecha'], datos['hora'], datos['docente'], datos['seccion'], datos['nivel'], datos['cupos'])

    return redirect(url_for('recepcionista_bp.vista_lista_sesiones'))

@recepcionista_bp.route('/sesiones/eliminar/<id>', methods=['GET'])
@token_requerido
def eliminar_sesion(datos_usuario, id):
    sesion = ServiciosSesion.eliminar(id)

    return redirect(url_for('recepcionista_bp.vista_lista_sesiones'))

@recepcionista_bp.route('/sesiones/dia', methods = ['GET'])
@token_requerido
def vista_lista_sesiones_dia(datos_usuario):
    
    fecha_actual = datetime.now()
    dia_hoy = fecha_actual.strftime("%A")
    hora_actual = fecha_actual.strftime("%H:%M") 
    fecha_actual = fecha_actual.strftime("%Y-%m-%d")
    
    dias_espanol = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miercoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sabado',
        'Sunday': 'Domingo'
    }

    dia_actual = dias_espanol[dia_hoy]
    fecha_actual = '2025-03-14'
    dia_actual = 'Viernes'
    print(dia_actual)
    print(fecha_actual)
    docentes = ServiciosDocente.obtener_por_dia(dia_actual)
    print('/*-'*100)
    print(docentes)
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    lista_horas = ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00', '22:30']

    sesiones = ServiciosSesion.obtener_por_fecha(fecha_actual)

    #pruebaa docentes

    docentes = ServiciosDocente.obtener_sesiones_por_fecha(fecha_actual)

    docentes_horarios = ServiciosDocente.obtener_todos()



    print(sesiones)
    return render_template('recepcionista/sesion_dia.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes, sesiones = sesiones, dia_actual = dia_actual, fecha_actual = fecha_actual, lista_horas = lista_horas, docentes_horarios = docentes_horarios, hora_actual = hora_actual)




#----------------------------------- GESTION ESTUDIANTES ------------------------------------------------
@recepcionista_bp.route('/usuarios/estudiantes', methods=['GET'])
@token_requerido
def vista_lista_estudiantes(datos_usuario):
    estudiantes = ServiciosEstudiante.obtener_todos()
    primer_nombre = datos_usuario.get('primer_nombre', 'Usuario')
    primer_apellido = datos_usuario.get('primer_apellido', '')

    

    return render_template('recepcionista/estudiantes.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, estudiantes = estudiantes)


@recepcionista_bp.route('/estudiantes/crear', methods = ['POST'])
@token_requerido
def crear_estudiante(datos_usuario):
    datos = request.form

    estudiante = ServiciosEstudiante.crear(datos['nombre_usuario'],
                                           datos['contrasena'],
                                           datos['correo'],
                                           datos['nombres'],
                                           datos['apellidos'],
                                           datos['carnet'],
                                           datos['telefono'],
                                           datos['telefono_titular'],
                                           datos['nombres_titular'],
                                           datos['nombre_nivel'],
                                           datos['rango_nivel'],
                                           datos['departamento_carnet'],
                                           datos.get('ocupacion_tutor', ''),  
                                           datos.get('parentesco_tutor', ''),
                                           datos.get('numero_cuenta', ''),
                                           datos.get('numero_contrato', ''),
                                           datos.get('inicio_contrato', ''),
                                           datos.get('fin_contrato', '')
                                           
                                           )
    
    return redirect(url_for('recepcionista_bp.vista_lista_estudiantes'))
#----------------------------------- GESTION ACTIVIDADES ------------------------------------------------

@recepcionista_bp.route('/actividades', methods=['GET'])
@token_requerido
def vista_lista_actividades(datos_usuario):
    actividades = ServiciosActividad.obtener_todos()
    docentes = ServiciosDocente.obtener_todos()
    print('/*-'*100)
    print(actividades)
    fecha = datos_usuario.get('fecha')
    hora = datos_usuario.get('hora')

    return render_template('recepcionista/actividades.html', fecha = fecha, hora = hora, actividades = actividades, docentes = docentes)


@recepcionista_bp.route('/actividades/crear', methods=['POST'])
@token_requerido
def crear_actividad(datos_usuario):
    datos = request.form

    actividades = ServiciosActividad.crear(datos['fecha'],
                                           datos['hora'],
                                           datos['docente'],
                                           datos['descripcion'],
                                           datos['nivel'],
                                           datos['cupos'] )
    print(actividades)
    mensaje = actividades.status
    if mensaje == 'success':
        flash('Éxito', "success")
    else: flash('Fracaso', "error")

    return redirect(url_for('recepcionista_bp.vista_lista_actividades'))



