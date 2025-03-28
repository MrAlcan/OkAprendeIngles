from app.models.usuario import Usuario
from app.config.extensiones import db
from app.serializer.serializadorUniversal import SerializadorUniversal

class ServiciosUsuario():

    def obtener_todos():
        datos = Usuario.query.all()
        datos_requeridos = ['id_usuario', 'nombres', 'apellidos', 'rol', 'activo']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        return respuesta

    def activar_usuario(id_usuario):
        usuario = Usuario.query.get(id_usuario)
        if usuario:
            usuario.activo = 1
            db.session.commit()
        
        return {"status": "success", "message": "Usuario activado exitosamente"}
    
    def desactivar_usuario(id_usuario):
        usuario = Usuario.query.get(id_usuario)
        if usuario:
            usuario.activo = 0
            db.session.commit()
        
        return {"status": "success", "message": "Usuario desactivado exitosamente"}