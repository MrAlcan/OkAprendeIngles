from app.models.administrador import Administrador
from app.config.extensiones import db, bcrypt
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
        datos = Administrador.query.filter_by(activo = 1)
        datos_requeridos = ['id_administrador', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'telefono_personal']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        return respuesta
    
    def modificar_contrasena(id, contrasena_antigua, contrasena_nueva):
        administrador = Administrador.query.get(id)
        if administrador:
            contrasena_hash = administrador.contrasena_hash
            resultado = bcrypt.check_password_hash(contrasena_hash, contrasena_antigua)
            if resultado:
                nueva_contrasena_hash = bcrypt.generate_password_hash(contrasena_antigua).decode('utf-8')
                administrador.contrasena_hash = nueva_contrasena_hash
                db.session.commit()
            else:
                return "contrasena no coincide"
        else:
            return "no se encontro el administrador"
