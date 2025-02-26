from app.models.actividad import Actividad
from app.config.extensiones import db
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal


class ServiciosActividad():

    def crear(fecha, hora, docente, descripcion, nivel, cupos):
        try:
            nueva_actividad = Actividad(fecha, hora, docente, descripcion, nivel, cupos)
            db.session.add(nueva_actividad)
            db.session.commit()
            return {"status": "success", "message": "Actividad creado exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
    
    def obtener_todos():
        datos = Actividad.query.all()
        datos_requeridos = ['id_actividad', 'fecha', 'hora', 'id_docente', 'descripcion', 'nivel', 'cupos_disponibles']
        respuesta = SerializadorUniversal.serializar_lista(datos=datos, campos_requeridos = datos_requeridos)
        return respuesta
    
    def obtener_por_id(id):
        dato = Actividad.query.get(id)
        datos_requeridos = ['id_actividad', 'fecha', 'hora', 'id_docente', 'descripcion', 'nivel', 'cupos_disponibles']
        respuesta = SerializadorUniversal.serializar_unico(dato=dato, campos_requeridos= datos_requeridos)
        return respuesta

    def obtener_por_docente(id_docentesdasdas):
        datos = Actividad.query.filter_by(id_docente = id_docentesdasdas)
        datos_requeridos = ['id_actividad', 'fecha', 'hora', 'id_docente', 'descripcion', 'nivel', 'cupos_disponibles']
        respuesta = SerializadorUniversal.serializar_lista(datos=datos, campos_requeridos= datos_requeridos)
        return respuesta