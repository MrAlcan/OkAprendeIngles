from flask import Blueprint, request, jsonify

autenticar_bp = Blueprint('autenticar_bp', __name__)

@autenticar_bp.route('/autenticar_credenciales', methods=['POST'])
def autenticar_credenciales():
    datos = request.form
    #nuevo_usuario = ServiciosUsuario.crear(nombre=datos['input_nombre_cuenta'], nombre_per=datos['input_nombres'],contrasena=datos['input_contrasena'],ap_paterno=datos['input_apellido_paterno'],ap_materno=datos['input_apellido_materno'],cargo=datos['input_cargo'],carnet=datos['input_carnet'],id_rol=datos['input_rol'])
    
    return jsonify({'mensaje': 'jio'}), 201