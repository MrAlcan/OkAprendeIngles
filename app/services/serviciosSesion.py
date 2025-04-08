from app.models.sesion import Sesion
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.config.extensiones import db

class ServiciosSesion():

    def obtener_todos():
        datos = Sesion.query.filter_by(activo = 1)

        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'id_docente', 'seccion', 'nivel', 'cupos_disponibles', 'activo']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        return respuesta
    
    def obtener_por_id(id):
        datos = Sesion.query.filter(Sesion.activo==1, Sesion.id_sesion==id).first()
        
        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'id_docente', 'seccion', 'nivel', 'cupos_disponibles', 'activo', 'link', 'imagen_url']
        respuesta = SerializadorUniversal.serializar_unico(dato= datos, campos_requeridos= datos_requeridos)
        return respuesta
    
    def crear(fecha, hora, id_docente, seccion, nivel, cupos_disponibles):
        sesion = Sesion(fecha, hora, id_docente, seccion, nivel, cupos_disponibles)
        db.session.add(sesion)
        db.session.commit()

        return True
    
    def actualizar(id, fecha, hora, id_docente, seccion, nivel, cupos_disponibles):
        sesion = Sesion.query.get(id)

        sesion.fecha = fecha
        sesion.hora = hora
        sesion.id_docente = id_docente
        sesion.seccion = seccion
        sesion.nivel = nivel
        sesion.cupos_disponibles = cupos_disponibles

        db.session.commit()

        return True
    
    def eliminar(id):
        sesion = Sesion.query.get(id)

        sesion.activo = 0

        db.session.commit()

        return True
    
    def obtener_por_fecha(fecha):
        datos = Sesion.query.filter_by(activo = 1, fecha = fecha)

        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'id_docente', 'seccion', 'nivel', 'cupos_disponibles', 'activo']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        for fila in respuesta:
            fila['hora'] = fila['hora'].strftime("%H:%M")
        return respuesta
    
    def obtener_por_fecha_docente(fecha, docente):
        datos = Sesion.query.filter_by(activo = 1, fecha = fecha, id_docente = docente)
        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'id_docente', 'seccion', 'nivel', 'cupos_disponibles', 'activo']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        respuesta_diccionario = {}
        for fila in respuesta:
            fila['hora'] = fila['hora'].strftime("%H:%M")
            respuesta_diccionario[fila['hora']] = fila

        return respuesta_diccionario
    
    