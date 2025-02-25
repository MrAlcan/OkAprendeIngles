from flask import Blueprint, request, jsonify
from flask import Blueprint, render_template, request, redirect, url_for

inicio_bp = Blueprint('inicio_bp', __name__)

@inicio_bp.route('/', methods=['GET'])
def vista_pagina_inicio():
    #pagina de inico
    print("ingreso a la pagina de inicio")
    return jsonify({'mensaje': 'pagina de inicio'}), 201

@inicio_bp.route('/ingresar', methods=['GET'])
def vista_ingresar():
    #vista de formulario para ingresar
    print('ingresar usuario')
    return render_template('ingresar.html')