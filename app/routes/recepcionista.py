from flask import Blueprint, request, jsonify
from flask import render_template, request, redirect, url_for, flash, make_response, send_file
from app.services.serviciosAdministrador import serviciosAdministrador
from app.services.serviciosRecepcionista import ServiciosRecepcionista
from app.services.serviciosDocentes import ServiciosDocente
from app.services.serviciosAutenticacion import ServiciosAutenticacion, token_requerido
from app.services.serviciosUsuario import ServiciosUsuario
from app.services.serviciosSesion import ServiciosSesion
from app.services.serviciosActividad import ServiciosActividad
from app.services.serviciosEstudiante import ServiciosEstudiante
from app.services.serviciosReportes import ServiciosReportes
from app.services.serviciosReportesInformes import ServiciosReportesInformes
from app.services.serviciosReportesExcelInformes import ServiciosReportesExcelInformes
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
    docentes = ServiciosDocente.obtener_todos(True)
    print('/*-'*100)
    print(docentes)
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    sesiones = ServiciosSesion.obtener_todos()

    lista_docentes = {}
    for docente in docentes:
        lista_docentes[docente['id_docente']] = docente['nombres'] + " " + docente['apellidos']
    
    for sesion in sesiones:
        sesion['nombre_docente'] = lista_docentes[sesion['id_docente']]

    docentes = ServiciosDocente.obtener_todos()
        
    return render_template('recepcionista/sesiones.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes, sesiones = sesiones)

@recepcionista_bp.route('/sesiones/crear', methods=['POST'])
@token_requerido
def crear_sesion(datos_usuario):
    id_usuario = str(datos_usuario['id_usuario'])

    # Obtienes la URL de la página anterior
    referer = request.referrer

    

    datos = request.form

    sesion = ServiciosSesion.crear(datos['fecha'], datos['hora'], datos['docente'], datos['seccion'], datos['nivel'], datos['cupos'], datos['tipo_sesion'])

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

    sesion = ServiciosSesion.actualizar(id, datos['fecha'], datos['hora'], datos['docente'], datos['seccion'], datos['nivel'], datos['cupos'], datos['tipo_sesion'])

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
    
    # Asegúrate de que esta función devuelve un objeto con el atributo 'extension'
    recepcionista = ServiciosRecepcionista.obtener_por_id(['id_datos_usuario'])

    return render_template(
        'recepcionista/estudiantes.html',
        primer_nombre=primer_nombre,
        primer_apellido=primer_apellido,
        estudiantes=estudiantes,
        recepcionista=recepcionista  # 👈 Esta línea evita el error
    )


@recepcionista_bp.route('/estudiantes/crear', methods = ['POST'])
@token_requerido
def crear_estudiante(datos_usuario):
    datos = request.form

    nivel_correspondiente = datos['nivel_seccion_correspondiente']
    seccion_correspondiente = datos['seccion_correspondiente']

    estudiante = ServiciosEstudiante.crear(
                                           datos['correo'],
                                           datos['nombres'],
                                           datos['apellidos'],
                                           datos['carnet'],
                                           datos['telefono'],
                                           datos['celular_titular'],
                                           datos['nombres_titular'],
                                           datos['nombre_nivel'],
                                           datos['rango_nivel'],
                                           datos['departamento_carnet'],
                                           datos.get('ocupacion_titular', ''),  
                                           datos.get('parentesco_titular', ''),
                                           datos.get('numero_cuenta', ''),
                                           datos.get('numero_contrato', ''),
                                           datos.get('fecha_inicio_contrato', ''),
                                           datos.get('fecha_expiracion_contrato', ''),
                                           seccion_correspondiente,
                                           nivel_correspondiente
                                           
                                           )
    
    return redirect(url_for('recepcionista_bp.vista_lista_estudiantes'))

@recepcionista_bp.route('/editar/estudiante/<id>', methods=['POST'])
@token_requerido
def editar_estudiante(datos_usuario, id):
    datos = request.form
    nivel_correspondiente = datos['nivel_seccion_correspondiente']
    seccion_correspondiente = datos['seccion_correspondiente']

    estudiante = ServiciosEstudiante.actualizar(id, datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['nombres_titular'], datos.get('celular_titular'), datos.get('ocupacion_tutor'), seccion_correspondiente,
                                           nivel_correspondiente)

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
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    return render_template('recepcionista/actividades.html', fecha = fecha, hora = hora, actividades = actividades, docentes = docentes, primer_nombre = primer_nombre, primer_apellido = primer_apellido,)


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
    mensaje = actividades['status']

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

@recepcionista_bp.route('/actividades/estudiantes/<int:id_actividad>', methods=['GET'])
@token_requerido
def ver_estudiantes_inscritos(datos_usuario, id_actividad):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    estudiantes = ServiciosActividad.obtener_estudiantes_inscritos(id_actividad)
    actividad = ServiciosActividad.obtener_por_id(id_actividad)
    return render_template('recepcionista/estudiantes_inscritos.html', 
                           primer_nombre=primer_nombre, 
                           primer_apellido=primer_apellido, 
                           actividad=actividad, 
                           estudiantes=estudiantes)

@recepcionista_bp.route('/actividades/inscribir/<int:id_actividad>', methods=['POST'])
@token_requerido
def inscribir_estudiante(datos_usuario, id_actividad):
    # Aquí la lógica para inscribir a un estudiante en la actividad
    actividad = ServiciosActividad.obtener_por_id(id_actividad)
    if actividad and actividad.cupos > 0:
        # Inscripción
        estudiante = ServiciosEstudiante.obtener_estudiante(datos_usuario['id'])
        # Lógica para registrar al estudiante
        ServiciosActividad.inscribir_estudiante(actividad, estudiante)
        return redirect(url_for('recepcionista.ver_estudiantes_inscritos', id_actividad=id_actividad))
    else:
        # Manejo de error si no hay cupos
        flash("No hay cupos disponibles para esta actividad", 'error')
        return redirect(url_for('recepcionista.vista_lista_actividades'))

@recepcionista_bp.route('/actividades/eliminar/<int:id_actividad>', methods=['GET'])
@token_requerido
def eliminar_actividad(datos_usuario, id_actividad):
    actividad = ServiciosActividad.eliminar(id_actividad)
    return redirect(url_for('recepcionista_bp.vista_lista_actividades'))


@recepcionista_bp.route('/reportes', methods=['GET'])
@token_requerido
def vista_reportes(datos_usuario):
    estudiantes = ServiciosEstudiante.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    return render_template(
        'recepcionista/reportes.html',
        primer_nombre=primer_nombre,
        primer_apellido=primer_apellido, estudiantes=estudiantes
    )
@recepcionista_bp.route('/usuarios/estudiantes/pdf', methods=['GET'])
@token_requerido
def generar_pdf_estudiantes_completos(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosEstudiante.obtener_reporte_todos_estudiantes(nombre_usuario)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="informe_estudiantes.pdf"'

    return response

@recepcionista_bp.route('/usuarios/estudiantes/okcard/pdf/<id>', methods=['GET'])
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






@recepcionista_bp.route('/sesiones/pdf/<id>', methods=['GET'])
@token_requerido
def generar_reporte_sesion_pdf(datos_usuario, id):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportes.generar_reporte_de_sesion_pdf(nombre_usuario, id)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_sesion.pdf"'

    return response

@recepcionista_bp.route('/sesiones/fecha/pdf/<fecha>', methods=['GET'])
@token_requerido
def generar_reporte_sesion_dia_pdf(datos_usuario, fecha):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportes.generar_reporte_de_sesiones_por_dia_pdf(nombre_usuario, fecha)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_sesiones.pdf"'

    return response

@recepcionista_bp.route('/sesiones/semana/pdf/<fecha>', methods=['GET'])
@token_requerido
def generar_reporte_sesion_semana_pdf(datos_usuario, fecha):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportes.generar_reporte_de_sesiones_por_semana_pdf(nombre_usuario, fecha)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_sesiones.pdf"'

    return response

@recepcionista_bp.route('/sesiones/mes/pdf/<fecha>', methods=['GET'])
@token_requerido
def generar_reporte_sesion_mes_pdf(datos_usuario, fecha):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportes.generar_reporte_de_sesiones_por_mes_pdf(nombre_usuario, fecha)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_sesiones.pdf"'

    return response

#-------------------------------------------------------------------------------------------------------------
#------------------------------------ REPORTES SESIONES DOCENTES ---------------------------------------------
#-------------------------------------------------------------------------------------------------------------

@recepcionista_bp.route('/sesiones/fecha/docente/pdf/<fecha>/<id>', methods=['GET'])
@token_requerido
def generar_reporte_sesion_dia_docente_pdf(datos_usuario, fecha, id):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportes.generar_reporte_de_sesiones_por_dia_docente_pdf(nombre_usuario, fecha, id)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_sesiones.pdf"'

    return response

@recepcionista_bp.route('/sesiones/semana/docente/pdf/<fecha>/<id>', methods=['GET'])
@token_requerido
def generar_reporte_sesion_semana_docente_pdf(datos_usuario, fecha, id):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportes.generar_reporte_de_sesiones_por_semana_docente_pdf(nombre_usuario, fecha, id)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_sesiones.pdf"'

    return response

@recepcionista_bp.route('/sesiones/mes/docente/pdf/<fecha>/<id>', methods=['GET'])
@token_requerido
def generar_reporte_sesion_mes_docente_pdf(datos_usuario, fecha, id):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportes.generar_reporte_de_sesiones_por_mes_docente_pdf(nombre_usuario, fecha, id)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_sesiones.pdf"'

    return response

#-------------------------------------------------------------------------------------------------------------
#------------------------------------ REPORTES INFORMES  -----------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

@recepcionista_bp.route('/reportes/informe/mensual/<fecha>', methods=['GET'])
@token_requerido
def generar_reporte_informe_mensual_pdf(datos_usuario, fecha):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportesInformes.generar_informe_mensual_estudiantes_pdf(nombre_usuario, fecha)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_informe_mensual.pdf"'

    return response

@recepcionista_bp.route('/reportes/informe/carga/horaria/mensual/<fecha>', methods=['GET'])
@token_requerido
def generar_reporte_informe_carga_horaria_mensual_pdf(datos_usuario, fecha):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportesInformes.generar_informe_carga_horaria_docentes_mes_pdf(nombre_usuario, fecha)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_informe_mensual.pdf"'

    return response

@recepcionista_bp.route('/reportes/informe/carga/horaria/semana/<fecha>', methods=['GET'])
@token_requerido
def generar_reporte_informe_carga_horaria_semana_pdf(datos_usuario, fecha):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportesInformes.generar_informe_carga_horaria_docentes_semana_pdf(nombre_usuario, fecha)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_informe_mensual.pdf"'

    return response


@recepcionista_bp.route('/reportes/informe/carga/horaria/semana/detallado/<fecha>', methods=['GET'])
@token_requerido
def generar_reporte_informe_carga_horaria_semana_detallado_pdf(datos_usuario, fecha):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportesInformes.generar_informe_carga_horaria_docentes_semana_detallado_pdf(nombre_usuario, fecha)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_informe_mensual.pdf"'

    return response



#---------------------------------------------- VISTAS REPORTES ----------------------------------------------------
@recepcionista_bp.route('/sesiones/reportes', methods=['GET'])
@token_requerido
def vista_sesiones_reporte(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    id_administrador = datos_usuario['id_usuario']

    sesiones = ServiciosSesion.obtener_todos()

    docentes = ServiciosDocente.obtener_todos(True)
    lista_docentes = {}
    for docente in docentes:
        lista_docentes[docente['id_docente']] = docente['nombres'] + " " + docente['apellidos']
    
    for sesion in sesiones:
        sesion['nombre_docente'] = lista_docentes[sesion['id_docente']]
    
    docentes = ServiciosDocente.obtener_todos()
    
    return render_template('recepcionista/reporte_sesiones.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesiones = sesiones)


@recepcionista_bp.route('/docentes/reportes', methods=['GET'])
@token_requerido
def vista_docentes_reporte(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    id_administrador = datos_usuario['id_usuario']

    #sesiones = ServiciosSesion.obtener_todos()

    docentes = ServiciosDocente.obtener_todos()
    #lista_docentes = {}
    #for docente in docentes:
        #lista_docentes[docente['id_docente']] = docente['nombres'] + " " + docente['apellidos']
    
    #for sesion in sesiones:
        #sesion['nombre_docente'] = lista_docentes[sesion['id_docente']]

    return render_template('recepcionista/reporte_docentes.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes)



#-------------------------------------------------------------------------------------------------------------
#------------------------------------ REPORTES INFORMES  EXCELS -----------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

@recepcionista_bp.route('/reportes/excel/informe/mensual/<fecha>', methods=['GET'])
@token_requerido
def generar_reporte_informe_mensual_excel(datos_usuario, fecha):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportesExcelInformes.generar_informe_mensual_estudiantes_excel(nombre_usuario, fecha)

    '''response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_informe_mensual.pdf"'

    return response'''
    return send_file(buffer,
                     download_name="Reporte_Estudiantes.xlsx",
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@recepcionista_bp.route('/reportes/excel/informe/carga/horaria/mensual/<fecha>', methods=['GET'])
@token_requerido
def generar_reporte_informe_carga_horaria_mensual_excel(datos_usuario, fecha):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportesExcelInformes.generar_informe_carga_horaria_docentes_mes_excel(nombre_usuario, fecha)

    '''response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_informe_mensual.pdf"'

    return response'''
    return send_file(buffer,
                     download_name="Reporte_Carga_Horaria_Mensual.xlsx",
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@recepcionista_bp.route('/reportes/excel/informe/carga/horaria/semana/<fecha>', methods=['GET'])
@token_requerido
def generar_reporte_informe_carga_horaria_semana_excel(datos_usuario, fecha):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportesExcelInformes.generar_informe_carga_horaria_docentes_semana_excel(nombre_usuario, fecha)

    '''response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="reporte_informe_mensual.pdf"'

    return response'''
    return send_file(buffer,
                     download_name="Reporte_Carga_Horaria_Semanal.xlsx",
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@recepcionista_bp.route('/reportes/excel/informe/carga/horaria/semana/detallado/<fecha>', methods=['GET'])
@token_requerido
def generar_reporte_informe_carga_horaria_semana_detallado_excel(datos_usuario, fecha):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    nombre_usuario = nombres + " " + apellidos

    buffer = ServiciosReportesExcelInformes.generar_informe_carga_horaria_docentes_semana_detallado_excel(nombre_usuario, fecha)

    return send_file(buffer,
                     download_name="Reporte_Carga_Horaria_Semanal_Detallado.xlsx",
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')



#---------------------------------------------- VISTAS INFORMES ----------------------------------------------------
@recepcionista_bp.route('/sesiones/informes', methods=['GET'])
@token_requerido
def vista_sesiones_informes(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    id_administrador = datos_usuario['id_usuario']


    return render_template('recepcionista/informe_sesiones.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido)






@recepcionista_bp.route('/cancelar/estudiante/<id_estudiante>/<id_sesion>', methods=['GET'])
@token_requerido
def cancelar_inscripcion_estudiante(datos_usuario, id_estudiante, id_sesion):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    cancelado = ServiciosEstudiante.cancelar_registro(id_estudiante, id_sesion, 'Cancelado por Recepción')

    referer = request.referrer

    if referer:
        return redirect(referer)
    else:
        # Si no hay referencia, rediriges a una página predeterminada
        return redirect(url_for('recepcionista_bp.vista_lista_sesiones'))
    

@recepcionista_bp.route('/material', methods=['GET'])
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

    return render_template('recepcionista/material.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, enlaces_archivos=enlaces_archivos, enlaces_audios=enlaces_audios)


# --------------- ELIMINAR SESION ----------------

@recepcionista_bp.route('/cancelar/eliminar/estudiante/<id_estudiante>/<id_sesion>', methods=['GET'])
@token_requerido
def cancelar_eliminar_inscripcion_estudiante(datos_usuario, id_estudiante, id_sesion):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    cancelado = ServiciosEstudiante.eliminar_estudiante_de_sesion(id_estudiante, id_sesion)

    referer = request.referrer

    if referer:
        return redirect(referer)
    else:
        # Si no hay referencia, rediriges a una página predeterminada
        return redirect(url_for('recepcionista_bp.vista_lista_sesiones'))