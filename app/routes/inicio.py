from flask import Blueprint, request, jsonify, render_template, redirect, url_for, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies, verify_jwt_in_request, unset_jwt_cookies
from app.services.serviciosAutenticacion import ServiciosAutenticacion, no_iniciar_sesion

inicio_bp = Blueprint('inicio_bp', __name__)

@inicio_bp.route('/', methods=['GET'])
@no_iniciar_sesion
def vista_pagina_inicio():
    #pagina de inico
    print("ingreso a la pagina de inicio")
    return jsonify({'mensaje': 'pagina de inicio'}), 201

@inicio_bp.route('/ingresar', methods=['GET', 'POST'])
@no_iniciar_sesion
def vista_ingresar():
    #vista de formulario para ingresar
    print('ingresar usuario')
    if request.method == "POST":
        datos = request.form
        nombre_usuario = datos['nombre_usuario']
        contrasena = datos['contrasena']
        print(datos)

        respuesta_usuario, dato_usuario = ServiciosAutenticacion.autenticar_nombre_usuario(nombre_usuario)

        if not respuesta_usuario:
            return render_template('ingresar.html', usuario_mensaje = dato_usuario, nombre_usuario = nombre_usuario, contrasena = contrasena)
        
        respuesta_contrasena, dato_contrasena = ServiciosAutenticacion.autenticar_contrasena(dato_usuario, contrasena)

        if not respuesta_contrasena:
            return render_template('ingresar.html', contrasena_mensaje = dato_contrasena, nombre_usuario = nombre_usuario, contrasena = contrasena)
        
        print(f"bienvenido {dato_contrasena}")

        token = ServiciosAutenticacion.generar_token(dato_usuario)
        token = str(token)
        print(token)
        
        if str(dato_contrasena)=='administrador':
            #print(' es admin')
            resp = make_response(redirect(url_for('administrador_bp.vista_inicio')))
            #print(' make response normal ')
            #try:
            #    set_access_cookies(resp, token)
            #except Exception as e:
            #    print(f"Ocurrió un error: {e}")
            #print(' set access cookies normal ')
            #return resp
        elif str(dato_contrasena)=='recepcionista':
            resp = make_response(redirect(url_for('recepcionista_bp.vista_inicio')))
        elif str(dato_contrasena)=='docente':
            resp = make_response(redirect(url_for('docente_bp.vista_inicio')))
        else:
            resp = make_response(redirect(url_for('estudiante_bp.vista_inicio')))
        
        set_access_cookies(resp, token)
        return resp
        
        
        #return redirect(url_for('administrador_bp.vista_inicio'))


    return render_template('ingresar.html')

@inicio_bp.route('/cerrar_sesion', methods=['GET'])
@jwt_required()
def cerrar_sesion():
    resp = make_response(redirect(url_for('inicio_bp.vista_ingresar')))
    unset_jwt_cookies(resp)
    return resp