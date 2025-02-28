from app.models.docente import Docente
from app.models.horario import Horario
from app.config.extensiones import db
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal
from datetime import datetime

class ServiciosDocente():

    def crear(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, asignacion_tutor, dias, horas_inicio, horas_final):
        try:
            nuevo_docente = Docente(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, asignacion_tutor)
            db.session.add(nuevo_docente)
            db.session.commit()

            id_docente = nuevo_docente.id_docente

            horarios = []

            for i in range(0, len(dias), 1):
                hora_i = datetime.strptime(horas_inicio[i], '%H:%M').time()
                hora_f = datetime.strptime(horas_final[i], '%H:%M').time()
                
                nuevo_horario = Horario(id_docente, dias[i], hora_i, hora_f)
                horarios.append(nuevo_horario)
            
            db.session.add_all(horarios)
            db.session.commit()

            return {"status": "success", "message": "Docente y Horarios creados exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
    
    def actualizar(id_docente, nombre_usuario, correo, nombres, apellidos, carnet, telefono, asignacion_tutor, dias, horas_inicio, horas_final, horarios_eliminados, horarios_modificados, dias_modificados, horas_inicio_modificados, horas_final_modificados):
        try:
            docente = Docente.query.get(id_docente)

            docente.nombre_usuario = nombre_usuario
            docente.correo = correo
            docente.nombres = nombres
            docente.apellidos = apellidos
            docente.carnet_identidad = carnet
            docente.telefono = telefono
            docente.asignacion_tutor = asignacion_tutor

            #db.session.commit()

            horarios = []

            for i in range(0, len(dias), 1):
                hora_i = datetime.strptime(horas_inicio[i], '%H:%M').time()
                hora_f = datetime.strptime(horas_final[i], '%H:%M').time()
                
                nuevo_horario = Horario(id_docente, dias[i], hora_i, hora_f)
                horarios.append(nuevo_horario)
            db.session.add_all(horarios)


            for i in range(0, len(horarios_modificados), 1):
                hora_i = datetime.strptime(horas_inicio_modificados[i], '%H:%M').time()
                hora_f = datetime.strptime(horas_final_modificados[i], '%H:%M').time()

                horario = Horario.query.get(horarios_modificados[i])
                if horario:
                    horario.dia = dias_modificados[i]
                    horario.hora_inicio = hora_i
                    horario.hora_final = hora_f
            
            for i in range(0, len(horarios_eliminados), 1):
                horario = Horario.query.get(horarios_eliminados[i])
                if horario:
                    horario.activo = 0
            

            db.session.commit()

            return {"status": "success", "message": "Docente y Horarios modificados exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
    
    def eliminar(id_docente):
        docente = Docente.query.get(id_docente)

        if docente:
            docente.activo = 0
            db.session.commit()
        return {"status": "success", "message": "Docente eliminado exitosamente"}


        
    def obtener_todos():
        datos = Docente.query.filter_by(activo = 1)
        

        datos_requeridos = ['id_docente', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'asignacion_tutor']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        for docente in respuesta:
            horarios = Horario.query.filter_by(id_docente = docente['id_docente'], activo = 1).order_by(Horario.hora_inicio).all() # para descendente -> Horario.hora_inicio.desc()
            datos_requeridos_h = ['id_horario', 'dia', 'hora_inicio', 'hora_final']
            respuesta_h = SerializadorUniversal.serializar_lista(datos= horarios, campos_requeridos= datos_requeridos_h)
            horario_por_dia = {}
            for horario in respuesta_h:
                if horario['dia'] not in horario_por_dia:
                    horario_por_dia[horario['dia']] = []
                horario_por_dia[horario['dia']].append({
                    'id_horario' : horario['id_horario'],
                    'hora_inicio' : horario['hora_inicio'].strftime('%H:%M'),
                    'hora_final' : horario['hora_final'].strftime('%H:%M')
                })
            docente['horarios'] = horario_por_dia
        #print("-*-"*100)
        #print("imprimeindo horarios")
        #print(respuesta)
        

        return respuesta
