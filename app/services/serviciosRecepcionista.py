from app.models.recepcionista import Recepcionista
from app.config.extensiones import db
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal

class ServiciosRecepcionista():

    def crear(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, telefono_personal):
        try:
            nuevo_recepcionista = Recepcionista(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, telefono_personal)
            db.session.add(nuevo_recepcionista)
            db.session.commit()
            return {"status": "success", "message": "Recepcionista creado exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
        
    def obtener_todos():
        datos = Recepcionista.query.all()
        datos_requeridos = ['id_recepcionista', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'telefono_personal']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        return respuesta
        
    def actualizar(id_recepcionista, nombre_usuario, correo, nombres, apellidos, carnet, telefono):
        try:

            recepcionista = Recepcionista.query.get(id_recepcionista)
            recepcionista.nombre_usuario = nombre_usuario
            recepcionista.correo = correo
            recepcionista.nombres = nombres
            recepcionista.apellidos = apellidos
            recepcionista.carnet_identidad = carnet
            recepcionista.telefono = telefono
            
            db.session.commit()

            return {"status": "success", "message": "Recepcionistas modificadas exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
    
    def eliminar(id_recepcionista):
        recepcionista = Recepcionista.query.get(id_recepcionista)

        if recepcionista:
            recepcionista.activo = 0
            db.session.commit()
        return {"status": "success", "message": "Recepcionista eliminado exitosamente"}
