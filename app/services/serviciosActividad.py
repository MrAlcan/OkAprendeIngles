from app.models.actividad import Actividad
from app.models.detalleActividad import DetalleActividad
from app.models.estudiante import Estudiante
from app.config.extensiones import db
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal


class ServiciosActividad():

    def crear(fecha, hora, docente, descripcion, nivel, cupos):
        try:
            nueva_actividad = Actividad(fecha, hora, docente, descripcion, nivel, cupos)
            db.session.add(nueva_actividad)
            print(nueva_actividad.__dict__)
            db.session.commit()
            return {"status": "success", "message": "Actividad creado exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
    
    def obtener_todos():
        datos = Actividad.query.filter(Actividad.activo==1).all()
        datos_requeridos = ['id_actividad', 'fecha', 'hora', 'id_docente', 'descripcion', 'nivel', 'cupos_disponibles']
        respuesta = SerializadorUniversal.serializar_lista(datos=datos, campos_requeridos = datos_requeridos)
        return respuesta
    
    def obtener_por_id(id):
        dato = Actividad.query.get(id)
        datos_requeridos = ['id_actividad', 'fecha', 'hora', 'id_docente', 'descripcion', 'nivel', 'cupos_disponibles']
        respuesta = SerializadorUniversal.serializar_unico(dato=dato, campos_requeridos= datos_requeridos)
        return respuesta

    def obtener_por_docente(id_docentesdasdas):
        datos = Actividad.query.filter_by(id_docente=id_docente).all()
        datos_requeridos = ['id_actividad', 'fecha', 'hora', 'id_docente', 'descripcion', 'nivel', 'cupos_disponibles']
        respuesta = SerializadorUniversal.serializar_lista(datos=datos, campos_requeridos= datos_requeridos)
        return respuesta
    def obtener_estudiantes_inscritos(id_actividad):
        resultados = (
            db.session.query(DetalleActividad, Estudiante)
            .join(Estudiante, DetalleActividad.id_estudiante == Estudiante.id_estudiante)
            .filter(DetalleActividad.id_actividad == id_actividad, DetalleActividad.activo == 1)
            .all()
        )
        
        estudiantes_inscritos = []
        for detalle, estudiante in resultados:
            estudiantes_inscritos.append({
                'id_estudiante': estudiante.id_estudiante,
                'nombres': estudiante.primer_nombre + ' ' + estudiante.primer_apellido,
                'estado_registro': detalle.estado_registro,
                'calificacion': detalle.calificacion,
                'justificacion': detalle.justificacion
            })
        return estudiantes_inscritos
    
    

    def eliminar(id_actividad):
        actividad = Actividad.query.get(id_actividad)

        if actividad:
            actividad.activo = 0
            db.session.commit()
        return {"status": "success", "message": "Administrador eliminado exitosamente"}

    def inscribir(id_estudiante, id_actividad):
            try:
                actividad = Actividad.query.get(id_actividad)
                estudiante = Estudiante.query.get(id_estudiante)

                if not actividad or not estudiante:
                    return {"status": "error", "message": "Actividad o estudiante no encontrado"}

                if actividad.cupos_disponibles <= 0:
                    return {"status": "error", "message": "No hay cupos disponibles"}

                # Verificar si ya está inscrito
                ya_inscrito = DetalleActividad.query.filter_by(
                    id_actividad=id_actividad,
                    id_estudiante=id_estudiante,
                    activo=1
                ).first()

                if ya_inscrito:
                    return {"status": "warning", "message": "Ya estás inscrito en esta actividad"}

                # Crear nueva inscripción
                nueva_inscripcion = DetalleActividad(
                    id_actividad=id_actividad,
                    id_estudiante=id_estudiante,
                    estado_registro="Inscrito",  # Ajusta según tu modelo
                    activo=1
                )

                actividad.cupos_disponibles -= 1

                db.session.add(nueva_inscripcion)
                db.session.commit()

                return {"status": "success", "message": "Inscripción exitosa"}

            except Exception as e:
                db.session.rollback()
                return {"status": "error", "message": str(e)}