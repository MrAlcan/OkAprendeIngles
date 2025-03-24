from app.models.administrador import Administrador
from app.config.extensiones import db, bcrypt
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal

class serviciosAdministrador():

    def crear(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, telefono_personal, extension):
        try:
            nuevo_administrador = Administrador(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, telefono_personal, extension)
            db.session.add(nuevo_administrador)
            db.session.commit()
            return {"status": "success", "message": "Administrador creado exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
        
    def obtener_todos():
        datos = Administrador.query.filter_by(activo = 1)
        datos_requeridos = ['id_administrador', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'telefono_personal', 'extension']
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

    def actualizar(id_administrador, nombre_usuario, correo, nombres, apellidos, carnet, telefono):
        try:

            administrador = Administrador.query.get(id_administrador)
            administrador.nombre_usuario = nombre_usuario
            administrador.correo = correo
            administrador.nombres = nombres
            administrador.apellidos = apellidos
            administrador.carnet_identidad = carnet
            administrador.telefono = telefono
            
            db.session.commit()

            return {"status": "success", "message": "Administradores modificados exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
    
    def eliminar(id_administrador):
        administrador = Administrador.query.get(id_administrador)

        if administrador:
            administrador.activo = 0
            db.session.commit()
        return {"status": "success", "message": "Administrador eliminado exitosamente"}

