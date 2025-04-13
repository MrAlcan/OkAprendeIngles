from flask import Blueprint, request, jsonify

from flask import render_template, request, redirect, url_for, make_response, send_file
from app.services.serviciosAdministrador import serviciosAdministrador
from app.services.serviciosRecepcionista import ServiciosRecepcionista
from app.services.serviciosDocentes import ServiciosDocente
from app.services.serviciosAutenticacion import ServiciosAutenticacion, token_requerido
from app.services.serviciosUsuario import ServiciosUsuario
from app.services.serviciosSesion import ServiciosSesion
from app.services.serviciosEstudiante import ServiciosEstudiante
from app.services.serviciosReportes import ServiciosReportes
from app.services.serviciosReportesInformes import ServiciosReportesInformes
from app.services.serviciosReportesExcelInformes import ServiciosReportesExcelInformes
from datetime import datetime

administrador_bp = Blueprint('administrador_bp', __name__)

@administrador_bp.route('/obtener_todos', methods=['GET'])
@token_requerido
def obtener_administradores(datos_usuario):
    administradores = serviciosAdministrador.obtener_todos()
    #print(administradores)
    #return jsonify({'mensaje': administradores}), 201
    return render_template('administrador/tabla_muestra.html', datos = administradores)

@administrador_bp.route('/inicio', methods=['GET'])
@token_requerido
def vista_inicio(datos_usuario):
    nombres = datos_usuario['primer_nombre']
    apellidos = datos_usuario['primer_apellido']
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('administrador/inicio.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido)

@administrador_bp.route('/usuarios', methods=['GET'])
@token_requerido
def vista_lista_usuarios(datos_usuario):
    usuarios = ServiciosUsuario.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('administrador/usuarios.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, usuarios = usuarios)




@administrador_bp.route('/usuarios/habilitar/<id>', methods=['GET'])
@token_requerido
def habilitar_usuario(datos_usuario, id):
    usuario = ServiciosUsuario.activar_usuario(id)
    return redirect(url_for('administrador_bp.vista_lista_usuarios'))

@administrador_bp.route('/usuarios/deshabilitar/<id>', methods=['GET'])
@token_requerido
def deshabilitar_usuario(datos_usuario, id):
    usuario = ServiciosUsuario.desactivar_usuario(id)
    return redirect(url_for('administrador_bp.vista_lista_usuarios'))


@administrador_bp.route('/usuarios/administradores', methods=['GET'])
@token_requerido
def vista_lista_administradores(datos_usuario):
    administradores = serviciosAdministrador.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('administrador/administradores.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, administradores = administradores)

@administrador_bp.route('/crear/administrador', methods=['POST'])
@token_requerido
def crear_administrador(datos_usuario):
    datos = request.form

    nuevo_administrador = serviciosAdministrador.crear(datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['telefono_personal'], datos['departamento_carnet'])

    if nuevo_administrador:
        return redirect(url_for('administrador_bp.vista_lista_administradores'))
    else:
        return jsonify({'codigo': 400})
    
@administrador_bp.route('/usuarios/recepcionistas', methods=['GET'])
@token_requerido
def vista_lista_recepcionistas(datos_usuario):
    recepcionistas = ServiciosRecepcionista.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('administrador/recepcionistas.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, recepcionistas = recepcionistas, administrador=datos_usuario)

@administrador_bp.route('/crear/recepcionista', methods=['POST'])
@token_requerido
def crear_recepcionista(datos_usuario):
    datos = request.form

    nuevo_administrador = ServiciosRecepcionista.crear(datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['telefono_personal'], 'LP')

    if nuevo_administrador:
        return redirect(url_for('administrador_bp.vista_lista_recepcionistas'))
    else:
        return jsonify({'codigo': 400})

@administrador_bp.route('/usuarios/docentes', methods=['GET'])
@token_requerido
def vista_lista_docentes(datos_usuario):
    docentes = ServiciosDocente.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]
    return render_template('administrador/docentes.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes)

@administrador_bp.route('/crear/docente', methods=['POST'])
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


    nuevo_docente = ServiciosDocente.crear(datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['asignacion_tutor'], lista_dias, lista_horas_inicio, lista_horas_final, datos['color'], datos['departamento_carnet'])
    print(nuevo_docente)

    #nuevo_administrador = ServiciosRecepcionista.crear(datos['nombre_usuario'], datos['contrasena'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['telefono_personal'])
    #if nuevo_administrador:
    #    return redirect(url_for('administrador_bp.vista_lista_docentes'))
    #else:
    #    return jsonify({'codigo': 400})
    return redirect(url_for('administrador_bp.vista_lista_docentes'))

@administrador_bp.route('/editar/docente/<id>', methods=['POST'])
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

    
    
    return redirect(url_for('administrador_bp.vista_lista_docentes'))

@administrador_bp.route('/docente/eliminar/<id>', methods=['GET'])
@token_requerido
def eliminar_docente(datos_usuario, id):
    docente = ServiciosDocente.eliminar(id)
    return redirect(url_for('administrador_bp.vista_lista_docentes'))

@administrador_bp.route('/editar/recepcionista/<id>', methods=['POST'])
@token_requerido
def editar_recepcionista(datos_usuario, id):
    datos = request.form
    recepcionista = ServiciosRecepcionista.actualizar(id, datos['nombre_usuario'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'])

    return redirect(url_for('administrador_bp.vista_lista_recepcionistas'))

@administrador_bp.route('/recepcionista/eliminar/<id>', methods=['GET'])
@token_requerido
def eliminar_recepcionista(datos_usuario, id):
    recepcionista = ServiciosRecepcionista.eliminar(id)
    return redirect(url_for('administrador_bp.vista_lista_recepcionistas'))

@administrador_bp.route('/editar/administrador/<id>', methods=['POST'])
@token_requerido
def editar_administrador(datos_usuario, id):
    datos = request.form
    administrador = serviciosAdministrador.actualizar(id, datos['nombre_usuario'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'])

    return redirect(url_for('administrador_bp.vista_lista_administradores'))

@administrador_bp.route('/administradores/eliminar/<id>', methods=['GET'])
@token_requerido
def eliminar_administrador(datos_usuario, id):
    administrador = serviciosAdministrador.eliminar(id)
    return redirect(url_for('administrador_bp.vista_lista_administradores'))

# ----------------------- GESTION SESIONES ----------------------------------

@administrador_bp.route('/sesiones', methods=['GET'])
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

    lista_docentes = {}
    for docente in docentes:
        lista_docentes[docente['id_docente']] = docente['nombres'] + " " + docente['apellidos']
    
    for sesion in sesiones:
        sesion['nombre_docente'] = lista_docentes[sesion['id_docente']]

    return render_template('administrador/sesiones.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes, sesiones = sesiones)

@administrador_bp.route('/sesiones/crear', methods=['POST'])
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
        return redirect(url_for('administrador_bp.vista_lista_sesiones'))
    return redirect(url_for('administrador_bp.vista_lista_sesiones'))

@administrador_bp.route('/sesiones/editar/<id>', methods=['POST'])
@token_requerido
def editar_sesion(datos_usuario, id):
    datos = request.form

    sesion = ServiciosSesion.actualizar(id, datos['fecha'], datos['hora'], datos['docente'], datos['seccion'], datos['nivel'], datos['cupos'], datos['tipo_sesion'])

    return redirect(url_for('administrador_bp.vista_lista_sesiones'))

@administrador_bp.route('/sesiones/eliminar/<id>', methods=['GET'])
@token_requerido
def eliminar_sesion(datos_usuario, id):
    sesion = ServiciosSesion.eliminar(id)

    return redirect(url_for('administrador_bp.vista_lista_sesiones'))

@administrador_bp.route('/sesiones/dia', methods = ['GET'])
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

    lista_horas = ['07:30', '08:30', '09:30', '10:30', '11:30', '12:00', '12:30', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']

    sesiones = ServiciosSesion.obtener_por_fecha(fecha_actual)

    #pruebaa docentes

    docentes = ServiciosDocente.obtener_sesiones_por_fecha(fecha_actual)

    docentes_horarios = ServiciosDocente.obtener_todos()



    print(sesiones)
    return render_template('administrador/sesion_dia.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes, sesiones = sesiones, dia_actual = dia_actual, fecha_actual = fecha_actual, lista_horas = lista_horas, docentes_horarios = docentes_horarios, hora_actual = hora_actual)




#----------------------------------- GESTION ESTUDIANTES ------------------------------------------------
@administrador_bp.route('/usuarios/estudiantes', methods=['GET'])
@token_requerido
def vista_lista_estudiantes(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    estudiantes = ServiciosEstudiante.obtener_todos()
    print(estudiantes)

    return render_template('administrador/estudiantes.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, estudiantes = estudiantes, administrador=datos_usuario)


@administrador_bp.route('/estudiantes/crear', methods = ['POST'])
@token_requerido
def crear_estudiante(datos_usuario):
    datos = request.form

    estudiante = ServiciosEstudiante.crear(datos['correo'],
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
                                           datos.get('inicio_contrato', ''),
                                           datos.get('fin_contrato', '')
                                           )
    
    return redirect(url_for('administrador_bp.vista_lista_estudiantes'))

@administrador_bp.route('/editar/estudiante/<id>', methods=['POST'])
@token_requerido
def editar_estudiante(datos_usuario, id):
    datos = request.form

    estudiante = ServiciosEstudiante.actualizar(id, datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['nombres_titular'], datos.get('celular_titular'), datos.get('ocupacion_tutor'))

    return redirect(url_for('administrador_bp.vista_lista_estudiantes'))

@administrador_bp.route('/estudiante/eliminar/<id>', methods=['GET'])
@token_requerido
def eliminar_estudiante(datos_usuario, id):
    estudiante = ServiciosEstudiante.eliminar(id)
    return redirect(url_for('administrador_bp.vista_lista_estudiantes'))

# -------------------------------------- GESTION SESIONES SEMANALES ------------------------------------------
@administrador_bp.route('/sesiones/semana', methods=['GET', 'POST'])
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

        lista_horas = ['07:30', '08:30', '09:30', '10:30', '11:30', '12:00', '12:30', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']

        sesiones = ServiciosSesion.obtener_por_fecha(fecha_actual)

        #pruebaa docentes

        docentes = ServiciosDocente.obtener_sesiones_por_fecha(fecha_actual)

        docentes_horarios = ServiciosDocente.obtener_todos()



        print(sesiones)
        #return render_template('administrador/sesion_dia.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes, sesiones = sesiones, dia_actual = dia_actual, fecha_actual = fecha_actual, lista_horas = lista_horas, docentes_horarios = docentes_horarios, hora_actual = hora_actual)


        return render_template("administrador/sesion_semana.html", primer_nombre = primer_nombre, primer_apellido = primer_apellido, fechas_posibles=fechas_posibles, docentes = docentes, sesiones = sesiones, dia_actual = dia_actual, fecha_actual = fecha_actual, lista_horas = lista_horas, docentes_horarios = docentes_horarios, hora_actual = hora_actual, obtenido=True)

    return render_template("administrador/sesion_semana.html", primer_nombre = primer_nombre, primer_apellido = primer_apellido, fechas_posibles=fechas_posibles)


@administrador_bp.route('/sesiones/ver/<id>', methods=['GET'])
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
        return redirect(url_for("administrador_bp.vista_lista_sesiones"))
    
    #id_docente = sesion['id_docente']
    
    tareas = ServiciosDocente.obtener_tarea_por_sesion(id)
    
    detalle_sesion = ServiciosDocente.obtener_detalles_sesion(id)
    print(detalle_sesion)

    detalle_tarea = ServiciosDocente.obtener_detalle_tareas_por_sesion(id)

    estudiantes_disponibles = serviciosAdministrador.obtener_estudiantes_para_sesion(id)
    

    return render_template("administrador/ver_sesion.html", primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesion=sesion, detalle_sesion=detalle_sesion, tarea=tareas, detalle_tareas=detalle_tarea, estudiantes_disponibles = estudiantes_disponibles)

@administrador_bp.route('/sesiones/agregar/estudiante/<id>', methods=['POST'])
@token_requerido
def agregar_estudiante_manualmente(datos_usuario, id):
    id_est = request.form['estudiante']

    referer = request.referrer

    agregado = serviciosAdministrador.agregar_estudiante_manualmente(id, id_est)


    if referer:
        return redirect(referer)
    else:
        # Si no hay referencia, rediriges a una página predeterminada
        return redirect(url_for('administrador_bp.vista_lista_sesiones'))


# -------------------- generacion pdf's ----------------------------

@administrador_bp.route('/usuarios/estudiantes/pdf', methods=['GET'])
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

@administrador_bp.route('/usuarios/estudiantes/okcard/pdf/<id>', methods=['GET'])
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

@administrador_bp.route('/sesiones/pdf/<id>', methods=['GET'])
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

@administrador_bp.route('/sesiones/fecha/pdf/<fecha>', methods=['GET'])
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

@administrador_bp.route('/sesiones/semana/pdf/<fecha>', methods=['GET'])
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

@administrador_bp.route('/sesiones/mes/pdf/<fecha>', methods=['GET'])
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

@administrador_bp.route('/sesiones/fecha/docente/pdf/<fecha>/<id>', methods=['GET'])
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

@administrador_bp.route('/sesiones/semana/docente/pdf/<fecha>/<id>', methods=['GET'])
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

@administrador_bp.route('/sesiones/mes/docente/pdf/<fecha>/<id>', methods=['GET'])
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

@administrador_bp.route('/reportes/informe/mensual/<fecha>', methods=['GET'])
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


@administrador_bp.route('/reportes', methods=['GET'])
@token_requerido
def vista_reportes(datos_usuario):
    estudiantes = ServiciosEstudiante.obtener_todos()
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    return render_template(
        'administrador/reportes.html',
        primer_nombre=primer_nombre,
        primer_apellido=primer_apellido, estudiantes=estudiantes
    )


@administrador_bp.route('/reportes/informe/carga/horaria/mensual/<fecha>', methods=['GET'])
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

@administrador_bp.route('/reportes/informe/carga/horaria/semana/<fecha>', methods=['GET'])
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


@administrador_bp.route('/reportes/informe/carga/horaria/semana/detallado/<fecha>', methods=['GET'])
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
@administrador_bp.route('/sesiones/reportes', methods=['GET'])
@token_requerido
def vista_sesiones_reporte(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    id_administrador = datos_usuario['id_usuario']

    sesiones = ServiciosSesion.obtener_todos()

    docentes = ServiciosDocente.obtener_todos()
    lista_docentes = {}
    for docente in docentes:
        lista_docentes[docente['id_docente']] = docente['nombres'] + " " + docente['apellidos']
    
    for sesion in sesiones:
        sesion['nombre_docente'] = lista_docentes[sesion['id_docente']]

    return render_template('administrador/reporte_sesiones.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, sesiones = sesiones)


@administrador_bp.route('/docentes/reportes', methods=['GET'])
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

    return render_template('administrador/reporte_docentes.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes)



#-------------------------------------------------------------------------------------------------------------
#------------------------------------ REPORTES INFORMES  EXCELS -----------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

@administrador_bp.route('/reportes/excel/informe/mensual/<fecha>', methods=['GET'])
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


@administrador_bp.route('/reportes/excel/informe/carga/horaria/mensual/<fecha>', methods=['GET'])
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


@administrador_bp.route('/reportes/excel/informe/carga/horaria/semana/<fecha>', methods=['GET'])
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


@administrador_bp.route('/reportes/excel/informe/carga/horaria/semana/detallado/<fecha>', methods=['GET'])
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
@administrador_bp.route('/sesiones/informes', methods=['GET'])
@token_requerido
def vista_sesiones_informes(datos_usuario):
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])

    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    id_administrador = datos_usuario['id_usuario']


    return render_template('administrador/informe_sesiones.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido)



@administrador_bp.route('/perfil', methods=['GET'])
@token_requerido
def vista_perfil(datos_usuario):
    administrador = serviciosAdministrador.obtener_por_id(datos_usuario['id_usuario'])
    nombres = str(datos_usuario['primer_nombre'])
    apellidos = str(datos_usuario['primer_apellido'])
    primer_nombre = nombres.split(' ')[0]
    primer_apellido = apellidos.split(' ')[0]

    return render_template(
        'administrador/perfil.html',
        primer_nombre=primer_nombre,
        primer_apellido=primer_apellido, administrador=administrador
    )
