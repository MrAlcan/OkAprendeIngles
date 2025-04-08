from app.models.estudiante import Estudiante
from app.models.detalleSesion import DetalleSesion
from app.models.sesion import Sesion
from app.models.tarea import Tarea
from app.models.detalleTarea import DetalleTarea


from app.serializer.serializadorUniversal import SerializadorUniversal
from app.config.extensiones import db
from datetime import datetime, timedelta, date

class ServiciosEstudiante():


    def obtener_datos_sesion(sesion, estudiante):

        datos_sesion = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==sesion, DetalleSesion.id_estudiante == estudiante).first()

        if datos_sesion:
        
            datos_sesion_requeridos = ['id_inscritos_sesion', 'id_sesion', 'id_estudiante', 'estado_registro', 'calificacion', 'justificacion']
            
            respuesta_datos_sesion = SerializadorUniversal.serializar_unico(dato=datos_sesion, campos_requeridos=datos_sesion_requeridos)
            datos = Sesion.query.filter(Sesion.activo==1, Sesion.id_sesion==sesion).first()

            if datos:
            
                datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'link']
                respuesta = SerializadorUniversal.serializar_unico(dato= datos, campos_requeridos= datos_requeridos)
                return respuesta, respuesta_datos_sesion
            else:
                return None, None
        else:
            return None, None

    def crear(correo, nombres, apellidos, carnet, telefono, telefono_titular, nombres_titular, nombre_nivel, rango_nivel, extension, ocupacion_tutor, parentesco_tutor, numero_cuenta, numero_contrato, inicio_contrato, fin_contrato):


        primer_nombre = str(nombres).split(' ')[0]
        primer_apellido = str(apellidos).split(' ')[0]
        segundo_apellido = ''
        if len(str(apellidos).split(' '))>1:
            segundo_apellido = str(apellidos).split(' ')[1]
        primer_nombre = primer_nombre.upper()
        primer_apellido = primer_apellido.upper()
        segundo_apellido = segundo_apellido.upper()
        nombre_usuario = primer_nombre + "." + primer_apellido

        validacion = Estudiante.query.filter(Estudiante.nombre_usuario==nombre_usuario).first()
        if validacion:
            nombre_usuario = nombre_usuario + "." + segundo_apellido
            validacion_2 = Estudiante.query.filter(Estudiante.nombre_usuario==nombre_usuario).first()
            if validacion_2:
                numeracion = True
                contador = 0
                nombre_usuario = nombre_usuario + "."
                while numeracion:
                    contador = contador + 1
                    nombre_usuario_n = nombre_usuario + str(contador)
                    validacion_3 = Estudiante.query.filter(Estudiante.nombre_usuario==nombre_usuario_n).first()
                    if not validacion_3:
                        numeracion = False
                        nombre_usuario = nombre_usuario_n
                        break


        estudiante = Estudiante(nombre_usuario, str(carnet), correo, nombres, apellidos, carnet, telefono, telefono_titular, nombres_titular, nombre_nivel, rango_nivel, extension, ocupacion_tutor, parentesco_tutor, numero_cuenta, numero_contrato, inicio_contrato, fin_contrato)


        db.session.add(estudiante)
        db.session.commit()

        return True
    
    def obtener_todos():

        datos = Estudiante.query.filter_by(activo = 1)

        datos_requeridos = ['id_estudiante', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'celular_titular', 'nombres_titular', 'nombre_nivel', 'rango_nivel', 'speakout_completado', 'working_completado', 'essential_completado', 'welcome_completado', 'activo']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        return respuesta
        
    def obtener_progreso():

        datos = Estudiante.query.filter_by(activo = 1)

        datos_requeridos = ['id_estudiante', 'speakout_completado', 'working_completado', 'essential_completado', 'welcome_completado']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        return respuesta

    def inscribir_a_sesion(estudiante, sesion_id):

        estudiante_op = Estudiante.query.get(estudiante)
        

        sesion = Sesion.query.get(sesion_id)

        sesion.cupos_disponibles = int(sesion.cupos_disponibles) - 1

        seccion_s = sesion.seccion

        nivel_est = 0

        if seccion_s == 'Welcome':
            nivel_est = int(estudiante_op.welcome_completado)
        elif seccion_s == 'Working':
            nivel_est = int(estudiante_op.working_completado)
        elif seccion_s == 'Essential':
            nivel_est = int(estudiante_op.essential_completado)
        else:
            nivel_est = int(estudiante_op.speakout_completado)

        detalle_sesion = DetalleSesion(sesion_id, estudiante, nivel_est)

        db.session.add(detalle_sesion)

        
        db.session.commit()

        return True
    
    def cancelar_registro(estudiante, sesion, justificacion = None):
        detalle_sesion = DetalleSesion.query.filter_by(activo = 1, id_sesion = sesion, id_estudiante = estudiante).first()

        detalle_sesion.estado_registro = 'Cancelado'
        detalle_sesion.calificacion = 0.0

        sesion_modificada = Sesion.query.filter(Sesion.id_sesion==sesion).first()

        cupos = int(sesion_modificada.cupos_disponibles)
        cupos = cupos + 1
        sesion_modificada.cupos_disponibles = cupos

        if justificacion:

            detalle_sesion.justificacion = justificacion
        
        db.session.commit()

        return True
    
    def asignar_asistencias(lista_estudiantes, sesion):

        for clave, valor in lista_estudiantes.items():
            detalle_sesion = DetalleSesion.query.filter_by(activo = 1, id_sesion = sesion, id_estudiante=clave)
            detalle_sesion.estado_registro = valor
        
        db.session.commit()

        return True
    
    def asignar_notas(lista_estudiantes, sesion):
        for estudiante, nota in lista_estudiantes.items():
            detalle_sesion = DetalleSesion.query.filter_by(activo=1, id_sesion = sesion, id_estudiante = estudiante)
            detalle_sesion.calificacion = nota

        db.session.commit()

        return True
    
    def obtener_sesiones_disponibles(estudiante):

        fecha_actual = datetime.now()

        # hoy ida 23/03/2025 para pruebas
        #fecha_actual = fecha_actual - timedelta(days=1)
        # fin pruevas

        fecha_actual = fecha_actual + timedelta(minutes=30)

        

        estudiante_ob = Estudiante.query.filter_by(activo = 1, id_estudiante = estudiante).first()

        rango_nivel = estudiante_ob.rango_nivel
        speakout_completado = int(estudiante_ob.speakout_completado) + 1
        working_completado = int(estudiante_ob.working_completado) + 1
        essential_completado = int(estudiante_ob.essential_completado) + 1
        welcome_completado = int(estudiante_ob.welcome_completado)

        nivel_inferior = int(str(rango_nivel).split('-')[0])
        nivel_superior = int(str(rango_nivel).split('-')[1])

        sesiones_calendario = {'08:00': {}, '08:30': {},
                               '09:00': {}, '09:30': {},
                               '10:00': {}, '10:30': {},
                               '11:00': {}, '11:30': {},
                               '12:00': {}, '12:30': {},
                               '13:00': {}, '13:30': {},
                               '14:00': {}, '14:30': {},
                               '15:00': {}, '15:30': {},
                               '16:00': {}, '16:30': {},
                               '17:00': {}, '17:30': {},
                               '18:00': {}, '18:30': {},
                               '19:00': {}, '19:30': {},
                               '20:00': {}, '20:30': {},
                               '21:00': {}, '21:30': {},
                               '22:00': {}, '22:30': {}}
        
        sesiones_calendario = {}

        dias_fechas = {}

        
        #hora_control = datetime.strptime(hora_string, '%H:%M')

        hoy = date.today()
        # PRUEBAS 23/03/2025 PARA VER HORARIOS
        #hoy = hoy - timedelta(days=1)
        # DINT PRUEBAS
        dias_al_lunes = hoy.weekday()

        lunes = hoy - timedelta(days= dias_al_lunes)
        sabado = lunes + timedelta(days=5)


        dia_string = lunes.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = 'Lunes'
        fecha_aux = lunes + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = 'Martes'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = 'Miercoles'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = 'Jueves'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = 'Viernes'
        dia_string = sabado.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = 'Sabado'

        print(dias_fechas)

        lunes = lunes.strftime('%Y-%m-%d')
        sabado = sabado.strftime('%Y-%m-%d')

        
        

        '''import datetime

        # Obtener la fecha actual
        hoy = datetime.date.today()

        # Calcular cuántos días atrás fue el lunes (0 es lunes, 1 es martes, ..., 6 es domingo)
        dias_hasta_lunes = hoy.weekday()

        # Restar los días para llegar al lunes
        lunes = hoy - datetime.timedelta(days=dias_hasta_lunes)

        print("Fecha del lunes:", lunes)'''


        sesiones_disponibles = []

        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'activo']


        sesiones_inscritas = DetalleSesion.query.filter(DetalleSesion.id_estudiante == estudiante, DetalleSesion.activo==1).all()

        lista_sesiones_inscritos = []

        if sesiones_inscritas:
            for sesion_i in sesiones_inscritas:
                #if sesion_i.estado_registro != 'Asistio' and sesion_i.estado_registro != 'Cancelado':
                if sesion_i.estado_registro == 'Inscrito':
                    lista_sesiones_inscritos.append(int(sesion_i.id_sesion))



        sesiones = Sesion.query.filter(Sesion.fecha.between(hoy, sabado), Sesion.activo==1).all()



        
        no_inscrito_welcome = True
        no_inscrito_essential = True
        no_inscrito_working = True
        no_inscrito_speakout = True

        if sesiones:
            for sesion in sesiones:
                if int(sesion.id_sesion) in lista_sesiones_inscritos:
                    if sesion.seccion=='Welcome':
                        no_inscrito_welcome = False
                    elif sesion.seccion=='Working':
                        no_inscrito_working = False
                    elif sesion.seccion=='Essential':
                        no_inscrito_essential = False
                    else:
                        no_inscrito_speakout = False
        
        if sesiones:
            for sesion in sesiones:
                print(sesion)
                

                if int(sesion.id_sesion) not in lista_sesiones_inscritos:
                    hora_fecha_sesion = str(sesion.fecha.strftime("%Y-%m-%d")+" "+sesion.hora.strftime('%H:%M'))
                    hora_fecha_sesion = datetime.strptime(hora_fecha_sesion, "%Y-%m-%d %H:%M")
                    hora_fecha_sesion = hora_fecha_sesion + timedelta(minutes=20)
                    if sesion.seccion == 'Welcome' and hora_fecha_sesion>fecha_actual:
                        if welcome_completado==0 and no_inscrito_welcome:
                            sesiones_disponibles.append(sesion)

                            # aqui esta una logica que se repite
                            hora_string = sesion.hora.strftime('%H:%M')

                            if hora_string not in sesiones_calendario:
                                sesiones_calendario[hora_string] = {}
                            dia_sesion = sesion.fecha.strftime("%Y-%m-%d")
                            dia_sesion = dias_fechas[dia_sesion]

                            if dia_sesion not in sesiones_calendario[hora_string]:
                                sesiones_calendario[hora_string][dia_sesion] = []
                            
                            sesiones_calendario[hora_string][dia_sesion].append(SerializadorUniversal.serializar_unico(sesion, datos_requeridos))
                            # aqui esta una logica que se repite




                    else:
                        if sesion.seccion == 'Working' and no_inscrito_working and hora_fecha_sesion>fecha_actual:
                            nivel_sesion = [int(str(sesion.nivel).split('-')[0]), int(str(sesion.nivel).split('-')[1])]
                            cupos = int(sesion.cupos_disponibles)

                            

                            if(nivel_sesion[0] <= working_completado and working_completado <=nivel_sesion[1] and cupos>0):
                                sesiones_disponibles.append(sesion)

                                # aqui esta una logica que se repite
                                hora_string = sesion.hora.strftime('%H:%M')

                                if hora_string not in sesiones_calendario:
                                    sesiones_calendario[hora_string] = {}
                                dia_sesion = sesion.fecha.strftime("%Y-%m-%d")
                                dia_sesion = dias_fechas[dia_sesion]

                                if dia_sesion not in sesiones_calendario[hora_string]:
                                    sesiones_calendario[hora_string][dia_sesion] = []
                                
                                sesiones_calendario[hora_string][dia_sesion].append(SerializadorUniversal.serializar_unico(sesion, datos_requeridos))
                                # aqui esta una logica que se repite

                        elif sesion.seccion == 'Essential' and no_inscrito_essential and hora_fecha_sesion>fecha_actual:
                            nivel_sesion = [int(str(sesion.nivel).split('-')[0]), int(str(sesion.nivel).split('-')[1])]
                            cupos = int(sesion.cupos_disponibles)

                            if(nivel_sesion[0] <= essential_completado and essential_completado <=nivel_sesion[1] and cupos>0):
                                sesiones_disponibles.append(sesion)

                                # aqui esta una logica que se repite
                                hora_string = sesion.hora.strftime('%H:%M')

                                if hora_string not in sesiones_calendario:
                                    sesiones_calendario[hora_string] = {}
                                dia_sesion = sesion.fecha.strftime("%Y-%m-%d")
                                dia_sesion = dias_fechas[dia_sesion]

                                if dia_sesion not in sesiones_calendario[hora_string]:
                                    sesiones_calendario[hora_string][dia_sesion] = []
                                
                                sesiones_calendario[hora_string][dia_sesion].append(SerializadorUniversal.serializar_unico(sesion, datos_requeridos))
                                # aqui esta una logica que se repite
                        elif no_inscrito_speakout and hora_fecha_sesion>fecha_actual:
                            print('/*-'*150)
                            print(sesion.nivel)
                            print(str(sesion.nivel).split('-'))
                            nivel_sesion = [int(str(sesion.nivel).split('-')[0]), int(str(sesion.nivel).split('-')[1])]
                            cupos = int(sesion.cupos_disponibles)

                            if(nivel_sesion[0] <= speakout_completado and speakout_completado <=nivel_sesion[1] and cupos>0):
                                sesiones_disponibles.append(sesion)

                                # aqui esta una logica que se repite
                                hora_string = sesion.hora.strftime('%H:%M')

                                if hora_string not in sesiones_calendario:
                                    sesiones_calendario[hora_string] = {}
                                dia_sesion = sesion.fecha.strftime("%Y-%m-%d")
                                dia_sesion = dias_fechas[dia_sesion]

                                if dia_sesion not in sesiones_calendario[hora_string]:
                                    sesiones_calendario[hora_string][dia_sesion] = []
                                
                                sesiones_calendario[hora_string][dia_sesion].append(SerializadorUniversal.serializar_unico(sesion, datos_requeridos))
                                # aqui esta una logica que se repite
                else:
                    if sesion.seccion=='Welcome':
                        no_inscrito_welcome = False
                    elif sesion.seccion=='Working':
                        no_inscrito_working = False
                    elif sesion.seccion=='Essential':
                        no_inscrito_essential = False
                    else:
                        no_inscrito_speakout = False
            
            
            respuesta = SerializadorUniversal.serializar_lista(datos= sesiones_disponibles, campos_requeridos= datos_requeridos)
            hora_string = fecha_actual.strftime('%H:%M')
            dia_actual = dias_fechas[fecha_actual.strftime('%Y-%m-%d')]
            return respuesta, sesiones_calendario, hora_string, dia_actual, lunes, sabado
        else:
            hora_string = fecha_actual.strftime('%H:%M')
            dia_actual = dias_fechas[fecha_actual.strftime('%Y-%m-%d')]
            return None, None, hora_string, dia_actual, lunes, sabado
        





    def obtener_sesiones_inscritas(estudiante):

        fecha_actual = datetime.now()

        # hoy ida 23/03/2025 para pruebas
        #fecha_actual = fecha_actual - timedelta(days=1)
        # fin pruevas
        fecha_actual = fecha_actual + timedelta(minutes=30)

        

        estudiante_ob = Estudiante.query.filter_by(activo = 1, id_estudiante = estudiante).first()

        rango_nivel = estudiante_ob.rango_nivel
        speakout_completado = int(estudiante_ob.speakout_completado) + 1
        working_completado = int(estudiante_ob.working_completado) + 1
        essential_completado = int(estudiante_ob.essential_completado) + 1
        welcome_completado = int(estudiante_ob.welcome_completado)

        nivel_inferior = int(str(rango_nivel).split('-')[0])
        nivel_superior = int(str(rango_nivel).split('-')[1])

        sesiones_calendario = {'08:00': {}, '08:30': {},
                               '09:00': {}, '09:30': {},
                               '10:00': {}, '10:30': {},
                               '11:00': {}, '11:30': {},
                               '12:00': {}, '12:30': {},
                               '13:00': {}, '13:30': {},
                               '14:00': {}, '14:30': {},
                               '15:00': {}, '15:30': {},
                               '16:00': {}, '16:30': {},
                               '17:00': {}, '17:30': {},
                               '18:00': {}, '18:30': {},
                               '19:00': {}, '19:30': {},
                               '20:00': {}, '20:30': {},
                               '21:00': {}, '21:30': {},
                               '22:00': {}, '22:30': {}}
        
        sesiones_calendario = {}

        dias_fechas = {}

        
        #hora_control = datetime.strptime(hora_string, '%H:%M')

        hoy = date.today()
        # PRUEBAS 23/03/2025 PARA VER HORARIOS
        #hoy = hoy - timedelta(days=1)
        # DINT PRUEBAS
        dias_al_lunes = hoy.weekday()

        lunes = hoy - timedelta(days= dias_al_lunes)
        lunes_i = lunes
        sabado = lunes + timedelta(days=5)


        dia_string = lunes.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = 'Lunes'
        fecha_aux = lunes + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = 'Martes'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = 'Miercoles'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = 'Jueves'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = 'Viernes'
        dia_string = sabado.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = 'Sabado'

        print(dias_fechas)

        lunes = lunes.strftime('%Y-%m-%d')
        sabado = sabado.strftime('%Y-%m-%d')

        
        

        '''import datetime

        # Obtener la fecha actual
        hoy = datetime.date.today()

        # Calcular cuántos días atrás fue el lunes (0 es lunes, 1 es martes, ..., 6 es domingo)
        dias_hasta_lunes = hoy.weekday()

        # Restar los días para llegar al lunes
        lunes = hoy - datetime.timedelta(days=dias_hasta_lunes)

        print("Fecha del lunes:", lunes)'''


        sesiones_disponibles = []

        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'activo', 'link']


        sesiones_inscritas = DetalleSesion.query.filter(DetalleSesion.id_estudiante == estudiante, DetalleSesion.activo==1).all()

        lista_sesiones_inscritos = []

        if sesiones_inscritas:
            for sesion_i in sesiones_inscritas:
                #if sesion_i.estado_registro != 'Asistio' and sesion_i.estado_registro != 'Cancelado':
                if sesion_i.estado_registro == 'Inscrito' or sesion_i.estado_registro == 'Falto' or sesion_i.estado_registro == 'Asistio':
                    lista_sesiones_inscritos.append(int(sesion_i.id_sesion))
                    print(f"ingreso a la lista la sesion : {sesion_i.id_sesion}")



        sesiones = Sesion.query.filter(Sesion.fecha.between(lunes_i, sabado), Sesion.activo==1).all()



        
        
        
        if sesiones:
            for sesion in sesiones:
                print(sesion)
                

                if int(sesion.id_sesion) in lista_sesiones_inscritos:
                    hora_fecha_sesion = str(sesion.fecha.strftime("%Y-%m-%d")+" "+sesion.hora.strftime('%H:%M'))
                    hora_fecha_sesion = datetime.strptime(hora_fecha_sesion, "%Y-%m-%d %H:%M")
                    hora_fecha_sesion = hora_fecha_sesion + timedelta(minutes=20)
                    if sesion.seccion == 'Welcome': #and hora_fecha_sesion>fecha_actual:
                        #if welcome_completado==0:
                        sesiones_disponibles.append(sesion)

                            # aqui esta una logica que se repite
                        hora_string = sesion.hora.strftime('%H:%M')

                        if hora_string not in sesiones_calendario:
                            sesiones_calendario[hora_string] = {}
                        dia_sesion = sesion.fecha.strftime("%Y-%m-%d")
                        dia_sesion = dias_fechas[dia_sesion]

                        if dia_sesion not in sesiones_calendario[hora_string]:
                            sesiones_calendario[hora_string][dia_sesion] = []
                            
                        sesiones_calendario[hora_string][dia_sesion].append(SerializadorUniversal.serializar_unico(sesion, datos_requeridos))
                            # aqui esta una logica que se repite




                    else:
                        if sesion.seccion == 'Working':# and hora_fecha_sesion>fecha_actual:
                            nivel_sesion = [int(str(sesion.nivel).split('-')[0]), int(str(sesion.nivel).split('-')[1])]
                            cupos = int(sesion.cupos_disponibles)

                            

                            if(nivel_sesion[0] <= working_completado and working_completado <=nivel_sesion[1] and cupos>0):
                                sesiones_disponibles.append(sesion)

                                # aqui esta una logica que se repite
                                hora_string = sesion.hora.strftime('%H:%M')

                                if hora_string not in sesiones_calendario:
                                    sesiones_calendario[hora_string] = {}
                                dia_sesion = sesion.fecha.strftime("%Y-%m-%d")
                                dia_sesion = dias_fechas[dia_sesion]

                                if dia_sesion not in sesiones_calendario[hora_string]:
                                    sesiones_calendario[hora_string][dia_sesion] = []
                                
                                sesiones_calendario[hora_string][dia_sesion].append(SerializadorUniversal.serializar_unico(sesion, datos_requeridos))
                                # aqui esta una logica que se repite

                        elif sesion.seccion == 'Essential':# and hora_fecha_sesion>fecha_actual:
                            nivel_sesion = [int(str(sesion.nivel).split('-')[0]), int(str(sesion.nivel).split('-')[1])]
                            cupos = int(sesion.cupos_disponibles)

                            if(nivel_sesion[0] <= essential_completado and essential_completado <=nivel_sesion[1] and cupos>0):
                                sesiones_disponibles.append(sesion)

                                # aqui esta una logica que se repite
                                hora_string = sesion.hora.strftime('%H:%M')

                                if hora_string not in sesiones_calendario:
                                    sesiones_calendario[hora_string] = {}
                                dia_sesion = sesion.fecha.strftime("%Y-%m-%d")
                                dia_sesion = dias_fechas[dia_sesion]

                                if dia_sesion not in sesiones_calendario[hora_string]:
                                    sesiones_calendario[hora_string][dia_sesion] = []
                                
                                sesiones_calendario[hora_string][dia_sesion].append(SerializadorUniversal.serializar_unico(sesion, datos_requeridos))
                                # aqui esta una logica que se repite
                        else:#elif #hora_fecha_sesion>fecha_actual:
                            print('/*-'*150)
                            print(sesion.nivel)
                            print(str(sesion.nivel).split('-'))
                            nivel_sesion = [int(str(sesion.nivel).split('-')[0]), int(str(sesion.nivel).split('-')[1])]
                            cupos = int(sesion.cupos_disponibles)

                            if(nivel_sesion[0] <= speakout_completado and speakout_completado <=nivel_sesion[1] and cupos>0):
                                sesiones_disponibles.append(sesion)

                                # aqui esta una logica que se repite
                                hora_string = sesion.hora.strftime('%H:%M')

                                if hora_string not in sesiones_calendario:
                                    sesiones_calendario[hora_string] = {}
                                dia_sesion = sesion.fecha.strftime("%Y-%m-%d")
                                dia_sesion = dias_fechas[dia_sesion]

                                if dia_sesion not in sesiones_calendario[hora_string]:
                                    sesiones_calendario[hora_string][dia_sesion] = []
                                
                                sesiones_calendario[hora_string][dia_sesion].append(SerializadorUniversal.serializar_unico(sesion, datos_requeridos))
                                # aqui esta una logica que se repite
                
            
            
            respuesta = SerializadorUniversal.serializar_lista(datos= sesiones_disponibles, campos_requeridos= datos_requeridos)
            hora_string = fecha_actual.strftime('%H:%M')
            dia_actual = dias_fechas[fecha_actual.strftime('%Y-%m-%d')]
            return respuesta, sesiones_calendario, hora_string, dia_actual, lunes, sabado
        else:
            hora_string = fecha_actual.strftime('%H:%M')
            dia_actual = dias_fechas[fecha_actual.strftime('%Y-%m-%d')]
            return None, None, hora_string, dia_actual, lunes, sabado
        

    def obtener_tarea_por_sesion(sesion):
        tarea = Tarea.query.filter(Tarea.activo==1, Tarea.id_sesion==sesion).first()
        if tarea:
            datos_requeridos = ['id_tarea', 'descripcion', 'material_adicional']
            respuesta = SerializadorUniversal.serializar_unico(dato= tarea, campos_requeridos= datos_requeridos)
            return respuesta
        else:
            return None
        
    def agregar_tarea(sesion, estudiante, archivo):
        tarea = Tarea.query.filter(Tarea.activo==1, Tarea.id_sesion==sesion).first()
        if tarea:
            id_tarea = tarea.id_tarea
            detalle_tarea = DetalleTarea.query.filter(DetalleTarea.activo==1, DetalleTarea.id_tarea == id_tarea, DetalleTarea.id_estudiante==estudiante).first()
            if detalle_tarea:
                detalle_tarea.material_subido = archivo
                db.session.commit()
            else:
                nueva_tarea = DetalleTarea(id_tarea, estudiante, archivo)
                db.session.add(nueva_tarea)
                db.session.commit()
            return True
        else:
            return None
    
    def obtener_material_por_sesion(sesion, estudiante):
        tarea = Tarea.query.filter(Tarea.activo==1, Tarea.id_sesion==sesion).first()
        if tarea:
            id_tarea = tarea.id_tarea
            detalle_tarea = DetalleTarea.query.filter(DetalleTarea.activo==1, DetalleTarea.id_tarea == id_tarea, DetalleTarea.id_estudiante==estudiante).first()
            if detalle_tarea:
                return str(detalle_tarea.material_subido)
            else:
                return None
        else:
            return None


