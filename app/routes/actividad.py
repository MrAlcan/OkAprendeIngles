from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from app.services.serviciosActividad import ServiciosActividad
from app.services.serviciosAutenticacion import token_requerido

actividad_bp = Blueprint('actividad_bp', __name__)

# ------------------------- RUTAS ACTIVIDAD ----------------------------

@actividad_bp.route('/actividades', methods=['GET'])
@token_requerido
def obtener_actividades(datos_usuario):
    actividades = ServiciosActividad.obtener_todos()
    return jsonify(actividades)

@actividad_bp.route('/actividades/<int:id>', methods=['GET'])
@token_requerido
def obtener_actividad_por_id(datos_usuario, id):
    actividad = ServiciosActividad.obtener_por_id(id)
    if not actividad:
       return jsonify({"status": "error", "message": "Actividad no encontrada"}), 404
    return jsonify(actividad)

@actividad_bp.route('/actividades/docente/<int:id_docente>', methods=['GET'])
@token_requerido
def obtener_actividades_por_docente(datos_usuario, id_docente):
    actividades = ServiciosActividad.obtener_por_docente(id_docente)
    return jsonify(actividades)

@actividad_bp.route('/actividades/crear', methods=['POST'])
@token_requerido
def crear_actividad(datos_usuario):
    data = request.get_json()

    required_fields = ["fecha", "hora", "id_docente", "descripcion", "nivel", "cupos"]
    if not all(field in data for field in required_fields):
        return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400

    try:
        resultado = ServiciosActividad.crear(
            fecha=data["fecha"],
            hora=data["hora"],
            docente=data["id_docente"],
            descripcion=data["descripcion"],
            nivel=data["nivel"],
            cupos=data["cupos"]
        )
        return jsonify(resultado), 201  
    except Exception as e:  # ← Aquí estaba el error
        return jsonify({"status": "error", "message": f"Error al crear la actividad: {str(e)}"}), 500



# --------------------------- VISTA ACTIVIDADES ------------------------

@actividad_bp.route('/actividades/disponibles', methods=['GET'])
@token_requerido
def vista_actividades_disponibles(datos_usuario):
    primer_nombre = datos_usuario['primer_nombre'].split(' ')[0]
    primer_apellido = datos_usuario['primer_apellido'].split(' ')[0]

    actividades = ServiciosActividad.obtener_todos()
    return render_template('estudiante/actividades_disponibles.html', 
                           primer_nombre=primer_nombre, 
                           primer_apellido=primer_apellido, 
                           actividades=actividades)

@actividad_bp.route('/actividades/inscribirse/<int:id_actividad>', methods=['GET'])
@token_requerido
def inscribir_en_actividad(datos_usuario, id_actividad):
    id_estudiante = datos_usuario['id_usuario']
    
    # Aquí iría la lógica de inscripción a la actividad, por ahora solo redirige
    return redirect(url_for('actividad_bp.vista_actividades_disponibles'))
