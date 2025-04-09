from app.models.docente import Docente
from app.models.horario import Horario
from app.models.sesion import Sesion
from app.models.detalleSesion import DetalleSesion
from app.models.estudiante import Estudiante
from app.models.tarea import Tarea
from app.models.detalleTarea import DetalleTarea

from app.config.extensiones import db
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.services.serviciosSesion import ServiciosSesion
from datetime import datetime, timedelta

class ServiciosDocente():


    def crear(correo, nombres, apellidos, carnet, telefono, asignacion_tutor, dias, horas_inicio, horas_final, color, extension):
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


            nuevo_docente = Docente(nombre_usuario, str(carnet), correo, nombres, apellidos, carnet, telefono, color, asignacion_tutor, extension)

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



    def obtener_sesion_por_id(docente, sesion):
        datos = Sesion.query.filter(Sesion.activo==1, Sesion.id_docente==docente, Sesion.id_sesion==sesion).first()
        if datos:
            datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'tipo_virtual']
            respuesta = SerializadorUniversal.serializar_unico(dato= datos, campos_requeridos= datos_requeridos)
            
            return respuesta
        else:
            return None
    
    def obtener_sesiones_docente(docente):
        datos = Sesion.query.filter(Sesion.activo==1, Sesion.id_docente==docente).order_by(Sesion.fecha.desc(), Sesion.hora.desc()).all()
        if datos:
            datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'tipo_virtual']
            respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
            
            return respuesta
        else:
            return None
    
    def obtener_detalles_sesion(sesion):
        datos = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==sesion).all()
        
        inscritos = 0
        cancelados = 0
        asistieron = 0
        faltaron = 0

        detalle_sesion = {}

        detalle_sesion['estudiantes'] = []
        detalle_sesion['cancelados'] = []

        if datos:

            for dato in datos:
                id_estudiante = dato.id_estudiante
                estudiante = Estudiante.query.get(id_estudiante)
                diccionario_estudiante = {
                    'id_estudiante': estudiante.id_estudiante,
                    'nombres': estudiante.nombres,
                    'apellidos': estudiante.apellidos,
                    'calificacion': dato.calificacion,
                    'recomendacion': dato.recomendacion,
                    'estado': dato.estado_registro
                }
                inscritos = inscritos + 1
                if str(dato.estado_registro) == "Cancelado":
                    cancelados = cancelados + 1
                    detalle_sesion['cancelados'].append(diccionario_estudiante)
                else:
                    detalle_sesion['estudiantes'].append(diccionario_estudiante)
                
                if str(dato.estado_registro) == "Asistio":
                    asistieron = asistieron + 1
                elif str(dato.estado_registro) == "Falto":
                    faltaron = faltaron + 1
            
            detalle_sesion['inscritos'] = inscritos
            detalle_sesion['cancelados'] = cancelados
            detalle_sesion['asistieron'] = asistieron
            detalle_sesion['faltaron'] = faltaron
            return detalle_sesion
        else:
            return None
                
    def asignar_link(sesion, link):
        obj_sesion = Sesion.query.get(sesion)

        obj_sesion.link = link

        db.session.commit()

        return True
    
    def asignar_asistencias_notas(estudiantes, sesion):

        ob_sesion = Sesion.query.filter(Sesion.activo==1, Sesion.id_sesion==sesion).first()
        
        seccion_sesion = ob_sesion.seccion

        LIMITE_NOTA = 85

        for estudiante in estudiantes:
            detalle = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==sesion, DetalleSesion.id_estudiante==estudiante['id_estudiante']).first()
            estudiante_ob = Estudiante.query.get(estudiante['id_estudiante'])
            if detalle:
                detalle.estado_registro = 'Asistio'
                detalle.recomendacion = estudiante['recomendacion']
                detalle.calificacion = float(estudiante['nota'])

                if seccion_sesion == 'Welcome':
                    rango = str(estudiante_ob.rango_nivel)
                    nivel_inicial = int(rango.split('-')[0]) - 1
                    estudiante_ob.speakout_completado = nivel_inicial
                    estudiante_ob.working_completado = nivel_inicial
                    estudiante_ob.essential_completado = nivel_inicial
                    estudiante_ob.welcome_completado = 1
                    estudiante_ob.paso_examen = 1
                elif seccion_sesion == 'Working':
                    nivel = int(estudiante_ob.working_completado)
                    nivel = nivel + 1
                    if float(estudiante['nota'])>=LIMITE_NOTA:
                        estudiante_ob.working_completado = nivel
                        if nivel % 5 == 0:
                            estudiante_ob.paso_examen = 0
                elif seccion_sesion == 'Essential':
                    nivel = int(estudiante_ob.essential_completado)
                    nivel = nivel + 1
                    if float(estudiante['nota'])>=LIMITE_NOTA:
                        estudiante_ob.essential_completado = nivel
                        if nivel % 5 == 0:
                            estudiante_ob.paso_examen = 0
                elif seccion_sesion == 'Speak Out':
                    nivel = int(estudiante_ob.speakout_completado)
                    nivel = nivel + 1
                    if float(estudiante['nota'])>=LIMITE_NOTA:
                        estudiante_ob.speakout_completado = nivel
                        if nivel % 5 == 0:
                            estudiante_ob.paso_examen = 0
                elif seccion_sesion == 'Test Oral':
                    if float(estudiante['nota'])>=LIMITE_NOTA:
                        estudiante_ob.paso_examen = 1
                elif seccion_sesion == 'Test Mixto':
                    nivel = int(estudiante_ob.working_completado)
                    detalle_auxiliar = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_estudiante==estudiante['id_estudiante'], DetalleSesion.calificacion>=LIMITE_NOTA, DetalleSesion.nivel_seccion==nivel, DetalleSesion.id_sesion!=sesion).all()
                    if detalle_auxiliar:
                        if float(estudiante['nota'])>=LIMITE_NOTA:
                            estudiante_ob.paso_examen = 1
        

            
        db.session.commit()

        detalles = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==sesion, DetalleSesion.estado_registro=='Inscrito').all()

        if detalles:
            for detall in detalles:
                detall.estado_registro = 'Falto'
                detall.calificacion = 0
                detall.recomendacion = None

            db.session.commit()
        
        return True
    
    def subir_imagen(sesion, dir_imagen):
        obj_sesion = Sesion.query.get(sesion)
        if obj_sesion:
            obj_sesion.imagen_url = dir_imagen
            db.session.commit()
        return True
    
    def obtener_tarea_por_sesion(sesion):
        tarea = Tarea.query.filter(Tarea.activo==1, Tarea.id_sesion==sesion).first()

        if tarea:

            datos_requeridos = ['id_tarea', 'descripcion', 'material_adicional']
            respuesta = SerializadorUniversal.serializar_unico(dato= tarea, campos_requeridos= datos_requeridos)
            return respuesta
        else:
            return None
        


    
    def asignar_tarea(id, descripcion, documento=None):

        tarea_existente = Tarea.query.filter(Tarea.activo==1, Tarea.id_sesion==id).first()

        if tarea_existente:
            tarea_existente.descripcion = descripcion
            if documento:
                tarea_existente.material_adicional = documento
            db.session.commit()
            return True
        else:

            nueva_tarea = Tarea(id, descripcion, documento)
            db.session.add(nueva_tarea)
            db.session.commit()

            return True


        '''detalle_sesion = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id, DetalleSesion.estado_registro!='Cancelado').all()

        id_tarea = nueva_tarea.id_tarea

        if detalle_sesion:
            for detalle in detalle_sesion:
                id_estudiante = detalle.id_estudiante'''
        



    def obtener_detalle_tareas_por_sesion(sesion):
        tarea = Tarea.query.filter(Tarea.activo==1, Tarea.id_sesion==sesion).first()
        if tarea:
            id_tarea = tarea.id_tarea
            detalle_tarea = DetalleTarea.query.filter(DetalleTarea.activo==1, DetalleTarea.id_tarea == id_tarea).all()

            if detalle_tarea:

                respuesta = []

                for det_tar in detalle_tarea:
                    id_est = det_tar.id_estudiante

                    estudiante = Estudiante.query.get(id_est)

                    cuerpo = {
                        'id_estudiante': id_est,
                        'nombres': estudiante.nombres,
                        'apellidos': estudiante.apellidos,
                        'material_subido': det_tar.material_subido
                    }
                    respuesta.append(cuerpo)
                
                return respuesta
            else:
                return None



        else:
            return None