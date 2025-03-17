from flask import Blueprint, request, jsonify
from flask import render_template, request, redirect, url_for
from app.services.serviciosAdministrador import serviciosAdministrador
from app.services.serviciosRecepcionista import ServiciosRecepcionista
from app.services.serviciosDocentes import ServiciosDocente
from app.services.serviciosAutenticacion import ServiciosAutenticacion, token_requerido
from app.services.serviciosUsuario import ServiciosUsuario

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
    nuevo_administrador = serviciosAdministrador.crear(datos['nombre_usuario'], datos['contrasena'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['telefono_personal'])
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
    return render_template('administrador/recepcionistas.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, recepcionistas = recepcionistas)

@administrador_bp.route('/crear/recepcionista', methods=['POST'])
@token_requerido
def crear_recepcionista(datos_usuario):
    datos = request.form
    nuevo_administrador = ServiciosRecepcionista.crear(datos['nombre_usuario'], datos['contrasena'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['telefono_personal'])
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

    nuevo_docente = ServiciosDocente.crear(datos['nombre_usuario'], datos['contrasena'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['asignacion_tutor'], lista_dias, lista_horas_inicio, lista_horas_final)

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

    docente = ServiciosDocente.actualizar(id, datos['nombre_usuario'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'], datos['asignacion_tutor'], lista_dias, lista_horas_inicio, lista_horas_final, ids_horarios_eliminados, lista_ids_existentes_ordenados, lista_dias_existentes, lista_horas_inicio_existentes, lista_horas_final_existentes)

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
    administrador = ServiciosAdministrador.actualizar(id, datos['nombre_usuario'], datos['correo'], datos['nombres'], datos['apellidos'], datos['carnet'], datos['telefono'])

    return redirect(url_for('administrador_bp.vista_lista_administradores'))

@administrador_bp.route('/administtrador/eliminar/<id>', methods=['GET'])
@token_requerido
def eliminar_administrador(datos_usuario, id):
    administrador = ServiciosAdministrador.eliminar(id)
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
    return render_template('administrador/sesiones.html', primer_nombre = primer_nombre, primer_apellido = primer_apellido, docentes = docentes)
