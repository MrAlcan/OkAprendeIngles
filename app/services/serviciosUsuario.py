from app.models.usuario import Usuario
from app.models.administrador import Administrador
from app.models.recepcionista import Recepcionista
from app.models.docente import Docente
from app.models.estudiante import Estudiante

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
    
    def obtener_usuario_por_id(id_usuario):
        usuario = Usuario.query.filter(Usuario.activo==1, Usuario.id_usuario==id_usuario).first()

        if not usuario:
            return None
        
        rol_usuario = str(usuario.rol)
        
        datos_requeridos = []
        usuario_obj = None

        if rol_usuario == 'administrador':
            datos_requeridos = ['id_usuario', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'telefono_personal', 'extension']
            usuario_obj = Administrador.query.filter(Administrador.activo==1, Administrador.id_administrador == id_usuario).first()
        elif rol_usuario == 'recepcionista':
            datos_requeridos = ['id_usuario', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'telefono_personal', 'extension']
            usuario_obj = Recepcionista.query.filter(Recepcionista.activo==1, Recepcionista.id_recepcionista == id_usuario).first()
        elif rol_usuario == 'docente':
            datos_requeridos = ['id_usuario', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'asignacion_tutor', 'color', 'extension']
            usuario_obj = Docente.query.filter(Docente.activo==1, Docente.id_docente == id_usuario).first()
        elif rol_usuario == 'estudiante':
            datos_requeridos = ['id_usuario', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'celular_titular', 'nombres_titular', 'nombre_nivel', 'rango_nivel', 'speakout_completado', 'working_completado', 'essential_completado', 'welcome_completado', 'activo', 'paso_examen', 'extension', 'ocupacion_tutor', 'parentesco_tutor', 'numero_cuenta', 'numero_contrato', 'inicio_contrato', 'fin_contrato']
    
            usuario_obj = Estudiante.query.filter(Estudiante.activo==1, Estudiante.id_estudiante == id_usuario).first()
        
        if not usuario_obj:
            return None
        
        respuesta = SerializadorUniversal.serializar_unico(usuario_obj, datos_requeridos)

        return respuesta
    
    def configurar_usuario_por_id(id_usuario, nombres, apellidos, correo, telefono):
        usuario = Usuario.query.filter(Usuario.activo==1, Usuario.id_usuario == id_usuario).first()

        if not usuario:
            return None
        
        usuario.nombres = nombres
        usuario.apellidos = apellidos
        usuario.telefono = telefono
        usuario.correo = correo

        db.session.commit()
        return True

            