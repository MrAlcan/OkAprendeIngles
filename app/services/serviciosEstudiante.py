from app.models.estudiante import Estudiante
from app.models.detalleSesion import DetalleSesion
from app.models.sesion import Sesion
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.config.extensiones import db
from datetime import datetime, timedelta, date

class ServiciosEstudiante():

    def crear(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, telefono_titular, nombres_titular, nombre_nivel, rango_nivel, extension, ocupacion_tutor, parentesco_tutor, numero_cuenta, numero_contrato, inicio_contrato, fin_contrato):

        estudiante = Estudiante(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, telefono_titular, nombres_titular, nombre_nivel, rango_nivel, extension, ocupacion_tutor, parentesco_tutor, numero_cuenta, numero_contrato, inicio_contrato, fin_contrato)

        db.session.add(estudiante)
        db.session.commit()

        return True
    
    def obtener_todos():

        datos = Estudiante.query.filter_by(activo = 1)

        datos_requeridos = ['id_estudiante', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'celular_titular', 'nombres_titular', 'nombre_nivel', 'rango_nivel', 'speakout_completado', 'working_completado', 'essential_completado', 'welcome_completado', 'activo']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        return respuesta
        

    def inscribir_a_sesion(estudiante, sesion):
        detalle_sesion = DetalleSesion(sesion, estudiante)

        sesion = Sesion.query.get(sesion)

        sesion.cupos_disponibles = int(sesion.cupos_disponibles) - 1

        db.session.add(detalle_sesion)

        
        db.session.commit()

        return True
    
    def cancelar_registro(estudiante, sesion, justificacion = None):
        detalle_sesion = DetalleSesion.query.filter_by(activo = 1, id_sesion = sesion, id_estudiante = estudiante).first()

        detalle_sesion.estado_registro = 'Cancelado'
        detalle_sesion.calificacion = 0.0

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
        fecha_actual = fecha_actual + timedelta(minutes=30)

        estudiante_ob = Estudiante.query.filter_by(activo = 1, id_estudiante = estudiante).first()

        rango_nivel = estudiante_ob.rango_nivel
        speakout_completado = int(estudiante_ob.speakout_completado)
        working_completado = int(estudiante_ob.working_completado)
        essential_completado = int(estudiante_ob.essential_completado)
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


        sesiones_inscritas = DetalleSesion.query.filter_by(id_estudiante = estudiante)

        lista_sesiones_inscritos = []

        if sesiones_inscritas:
            for sesion_i in sesiones_inscritas:
                lista_sesiones_inscritos.append(int(sesion_i.id_sesion))



        sesiones = Sesion.query.filter(Sesion.fecha.between(hoy, sabado), Sesion.activo==1).all()

        if sesiones:
            for sesion in sesiones:
                if int(sesion.id_sesion) not in lista_sesiones_inscritos:
                    if sesion.seccion == 'Welcome':
                        if welcome_completado==0:
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
                        if sesion.seccion == 'Working':
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

                        elif sesion.seccion == 'Essential':
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
                        else:
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
        



