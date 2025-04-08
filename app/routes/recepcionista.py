from flask import Blueprint, request, jsonify
from flask import render_template, request, redirect, url_for, flash
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
    nuevo_administrador = ServiciosRecepcionista.crear(datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['telefono_personal'], datos['departamento_carnet'])
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
    return render_template('recepcionista/docentes.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes)

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

    nuevo_docente = ServiciosDocente.crear(datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['asignacion_tutor'], lista_dias, lista_horas_inicio, lista_horas_final, datos['color'], 'LP')

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

    # Obtienes la URL de la página anterior
    referer = request.referrer

    

    datos = request.form

    sesion = ServiciosSesion.crear(datos['fecha'], datos['hora'], datos['docente'], datos['seccion'], datos['nivel'], datos['cupos'])

    # Rediriges al usuario a la página de donde vino
    if referer:
        return redirect(referer)
    else:
        # Si no hay referencia, rediriges a una página predeterminada
        return redirect(url_for('recepcionista_bp.vista_lista_sesiones'))
    return redirect(url_for('administrador_bp.vista_lista_sesiones'))

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

    return redirect(url_for('administrador_bp.vista_lista_sesiones'))

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
    #fecha_actual = '2025-03-24'
    #dia_actual = 'Lunes'
    print(dia_actual)
    print(fecha_actual)
    docentes = ServiciosDocente.obtener_por_dia(dia_actual)
    print('/*-'*100)
    print(docentes)
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    lista_horas = ['07:30', '08:30', '09:30', '10:30', '11:30', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']

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

    estudiante = ServiciosEstudiante.crear(
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



@recepcionista_bp.route('/sesiones/semana', methods=['GET', 'POST'])
@token_requerido
def vista_sesiones_semanales(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    id_administrador = datos_usuario['id_usuario']

    fechas_posibles = serviciosAdministrador.obtener_fechas_siguientes()

    if request.method == 'POST':
        fecha_seleccionada = str(request.form['fecha'])
        dias_espanol = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miercoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sabado',
            'Sunday': 'Domingo'
        }

        fecha_seleccionada = fecha_seleccionada + " 01:00:00"

        fecha_actual = datetime.strptime(fecha_seleccionada, "%Y-%m-%d %H:%M:%S")

        dia_hoy = fecha_actual.strftime("%A")
        hora_actual = fecha_actual.strftime("%H:%M") 
        fecha_actual = fecha_actual.strftime("%Y-%m-%d")

        dia_actual = dias_espanol[dia_hoy]
        #fecha_actual = '2025-03-24'
        #dia_actual = 'Lunes'
        print(dia_actual)
        print(fecha_actual)
        docentes = ServiciosDocente.obtener_por_dia(dia_actual)
        print('/*-'*100)
        print(docentes)
        nombres = str(datos_usuario['primer_nombre'])
        apellidos = str(datos_usuario['primer_apellido'])
        primer_nombre = nombres.split(' ')[0]
        primer_apellido = apellidos.split(' ')[0]

        lista_horas = ['07:30', '08:30', '09:30', '10:30', '11:30', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']

        sesiones = ServiciosSesion.obtener_por_fecha(fecha_actual)

        #pruebaa docentes

        docentes = ServiciosDocente.obtener_sesiones_por_fecha(fecha_actual)

        docentes_horarios = ServiciosDocente.obtener_todos()



        print(sesiones)
        #return render_template('administrador/sesion_dia.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes, sesiones = sesiones, dia_actual = dia_actual, fecha_actual = fecha_actual, lista_horas = lista_horas, docentes_horarios = docentes_horarios, hora_actual = hora_actual)


        return render_template("recepcionista/sesion_semana.html", primer_nombre = primer_nombre, primer_apellido = primer_apellido, fechas_posibles=fechas_posibles, docentes = docentes, sesiones = sesiones, dia_actual = dia_actual, fecha_actual = fecha_actual, lista_horas = lista_horas, docentes_horarios = docentes_horarios, hora_actual = hora_actual, obtenido=True)

    return render_template("recepcionista/sesion_semana.html", primer_nombre = primer_nombre, primer_apellido = primer_apellido, fechas_posibles=fechas_posibles)


@recepcionista_bp.route('/sesiones/ver/<id>', methods=['GET'])
@token_requerido
def vista_sesion_por_id(datos_usuario, id):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    id_administrador = datos_usuario['id_usuario']

    #sesion = ServiciosDocente.obtener_sesion_por_id(id_docente, id)

    sesion = ServiciosSesion.obtener_por_id(id)



    

    if not sesion:
        return redirect(url_for("recepcionista_bp.vista_lista_sesiones"))
    
    #id_docente = sesion['id_docente']
    
    tareas = ServiciosDocente.obtener_tarea_por_sesion(id)
    
    detalle_sesion = ServiciosDocente.obtener_detalles_sesion(id)
    print(detalle_sesion)

    detalle_tarea = ServiciosDocente.obtener_detalle_tareas_por_sesion(id)

    estudiantes_disponibles = serviciosAdministrador.obtener_estudiantes_para_sesion(id)
    

    return render_template("recepcionista/ver_sesion.html", primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesion=sesion, detalle_sesion=detalle_sesion, tarea=tareas, detalle_tareas=detalle_tarea, estudiantes_disponibles = estudiantes_disponibles)

@recepcionista_bp.route('/sesiones/agregar/estudiante/<id>', methods=['POST'])
@token_requerido
def agregar_estudiante_manualmente(datos_usuario, id):
    id_est = request.form['estudiante']

    referer = request.referrer

    agregado = serviciosAdministrador.agregar_estudiante_manualmente(id, id_est)


    if referer:
        return redirect(referer)
    else:
        # Si no hay referencia, rediriges a una página predeterminada
        return redirect(url_for('recepcionista_bp.vista_lista_sesiones'))
