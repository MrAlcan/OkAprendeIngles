from flask import Blueprint, request, jsonify
from app.services.serviciosAdministrador import serviciosAdministrador

administrador_bp = Blueprint('administrador_bp', __name__)

@administrador_bp.route('/obtener_todos', methods=['GET'])
def obtener_administradores():
    administradores = serviciosAdministrador.obtener_todos()
    print(administradores)
    return jsonify({'mensaje': administradores}), 201