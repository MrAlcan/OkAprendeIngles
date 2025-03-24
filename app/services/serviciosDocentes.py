from app.models.docente import Docente
from app.models.horario import Horario

from app.config.extensiones import db
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.services.serviciosSesion import ServiciosSesion
from datetime import datetime, timedelta

class ServiciosDocente():

    def crear(correo, nombres, apellidos, carnet, telefono, asignacion_tutor, dias, horas_inicio, horas_final, color):
        try:
            primer_nombre = str(nombres).split(' ')[0]
            primer_apellido = str(apellidos).split(' ')[0]
            segundo_apellido = ''
            if len(str(apellidos).split(' '))>1:
                segundo_apellido = str(apellidos).split(' ')[1]
            primer_nombre = primer_nombre.upper()
            primer_apellido = primer_apellido.upper()
            segundo_apellido = segundo_apellido.upper()
            nombre_usuario = primer_nombre + "." + primer_apellido

            validacion = Docente.query.filter(Docente.nombre_usuario==nombre_usuario).first()
            if validacion:
                nombre_usuario = nombre_usuario + "." + segundo_apellido
                validacion_2 = Docente.query.filter(Docente.nombre_usuario==nombre_usuario).first()
                if validacion_2:
                    numeracion = True
                    contador = 0
                    nombre_usuario = nombre_usuario + "."
                    while numeracion:
                        contador = contador + 1
                        nombre_usuario_n = nombre_usuario + str(contador)
                        validacion_3 = Docente.query.filter(Docente.nombre_usuario==nombre_usuario_n).first()
                        if not validacion_3:
                            numeracion = False
                            nombre_usuario = nombre_usuario_n
                            break


            nuevo_docente = Docente(nombre_usuario, str(carnet), correo, nombres, apellidos, carnet, telefono, color, asignacion_tutor)
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
    
    def actualizar(id_docente, nombre_usuario, correo, nombres, apellidos, carnet, telefono, asignacion_tutor, dias, horas_inicio, horas_final, horarios_eliminados, horarios_modificados, dias_modificados, horas_inicio_modificados, horas_final_modificados, color):
        try:
            docente = Docente.query.get(id_docente)

            docente.nombre_usuario = nombre_usuario
            docente.correo = correo
            docente.nombres = nombres
            docente.apellidos = apellidos
            docente.carnet_identidad = carnet
            docente.telefono = telefono
            docente.asignacion_tutor = asignacion_tutor
            docente.color = color

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
        

        datos_requeridos = ['id_docente', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'asignacion_tutor', 'color']
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
    
    def obtener_por_dia(dia):
        datos = Docente.query.filter_by(activo = 1)

        datos_requeridos = ['id_docente', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'asignacion_tutor', 'color']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        
        for docente in respuesta:
            horarios = Horario.query.filter_by(id_docente = docente['id_docente'], activo = 1, dia=dia).order_by(Horario.hora_inicio).all() # para descendente -> Horario.hora_inicio.desc()
            datos_requeridos_h = ['id_horario', 'dia', 'hora_inicio', 'hora_final']
            respuesta_h = SerializadorUniversal.serializar_lista(datos= horarios, campos_requeridos= datos_requeridos_h)
            #print(respuesta_h)
            horario_por_dia = []
            if respuesta_h:
                for horario in respuesta_h:
                    
                    horario_por_dia.append({
                        'id_horario' : horario['id_horario'],
                        'hora_inicio' : horario['hora_inicio'].strftime('%H:%M'),
                        'hora_final' : horario['hora_final'].strftime('%H:%M')
                    })
                docente['horarios'] = horario_por_dia
            else:
                docente['horarios'] = []
        
        return respuesta
    
    def obtener_sesiones_por_fecha(fecha):

        fecha_format = datetime.strptime(fecha, "%Y-%m-%d")

        dia_hoy = fecha_format.strftime("%A")
        
        dias_espanol = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miercoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sabado',
            'Sunday': 'Domingo'
        }

        dia = dias_espanol[dia_hoy]

        datos = Docente.query.filter_by(activo = 1)

        #sesiones = ServiciosSesion.obtener_por_fecha(fecha)

        datos_requeridos = ['id_docente', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'asignacion_tutor', 'color']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        
        for docente in respuesta:
            horarios = Horario.query.filter_by(id_docente = docente['id_docente'], activo = 1, dia=dia).order_by(Horario.hora_inicio).all() # para descendente -> Horario.hora_inicio.desc()
            datos_requeridos_h = ['id_horario', 'dia', 'hora_inicio', 'hora_final']
            respuesta_h = SerializadorUniversal.serializar_lista(datos= horarios, campos_requeridos= datos_requeridos_h)
            #print(respuesta_h)

            sesiones = ServiciosSesion.obtener_por_fecha_docente(fecha, docente['id_docente'])

            horario_por_dia = {}
            if respuesta_h:
                for horario in respuesta_h:

                    hora_inicio = horario['hora_inicio'].strftime('%H:%M')
                    hora_final = horario['hora_final'].strftime('%H:%M')

                    hora_inicio = datetime.strptime(hora_inicio, '%H:%M')
                    hora_final = datetime.strptime(hora_final, '%H:%M')

                    hora_control = hora_inicio

                    while hora_control<hora_final:
                        
                        hora_string = hora_control.strftime('%H:%M')

                        valor = sesiones.get(hora_string)
                        print(hora_string)
                        if valor is not None:
                            horario_por_dia[hora_string] = sesiones[hora_string]
                            hora_control = hora_control + timedelta(minutes=30)
                            hora_string = hora_control.strftime('%H:%M')
                            horario_por_dia[hora_string] = 'sesion'
                        else:
                            horario_por_dia[hora_string] = 'horario'
                        print(horario_por_dia)
                        hora_control = hora_control + timedelta(minutes=30)



                    
                    '''horario_por_dia.append({
                        'id_horario' : horario['id_horario'],
                        'hora_inicio' : horario['hora_inicio'].strftime('%H:%M'),
                        'hora_final' : horario['hora_final'].strftime('%H:%M')
                    })'''



                docente['horarios'] = horario_por_dia
            else:
                docente['horarios'] = None # []
        
        return respuesta
