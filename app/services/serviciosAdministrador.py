from app.models.administrador import Administrador
from app.config.extensiones import db
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal

class serviciosAdministrador():

    def crear(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, telefono_personal):
        try:
            nuevo_administrador = Administrador(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, telefono_personal)
            db.session.add(nuevo_administrador)
            db.session.commit()
            return {"status": "success", "message": "Administrador creado exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
        
    def obtener_todos():
        datos = Administrador.query.all()
        datos_requeridos = ['id_administrador', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'telefono_personal']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        return respuesta
