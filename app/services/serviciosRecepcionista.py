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
