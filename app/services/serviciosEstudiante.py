from app.models.estudiante import Estudiante
from app.models.detalleSesion import DetalleSesion
from app.models.detalleActividad import DetalleActividad
from app.models.sesion import Sesion
from app.models.tarea import Tarea
from app.models.detalleTarea import DetalleTarea
from app.models.actividad import Actividad
from app.models.docente import Docente

from app.services.serviciosCorreo import ServiciosCorreo

from sqlalchemy.exc import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.config.extensiones import db
from datetime import datetime, timedelta, date
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
import os


import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from datetime import datetime
import queue
from io import BytesIO

#logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
logo_direccion = os.path.join('var', 'www', 'OkAprendeIngles', 'app', 'static', 'img', 'logo.jpeg')

class ServiciosEstudiante():


    def obtener_datos_sesion(sesion, estudiante):

        datos_sesion = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==sesion, DetalleSesion.id_estudiante == estudiante).first()

        if datos_sesion:
        
            datos_sesion_requeridos = ['id_inscritos_sesion', 'id_sesion', 'id_estudiante', 'estado_registro', 'calificacion', 'justificacion']
            
            respuesta_datos_sesion = SerializadorUniversal.serializar_unico(dato=datos_sesion, campos_requeridos=datos_sesion_requeridos)
            datos = Sesion.query.filter(Sesion.activo==1, Sesion.id_sesion==sesion).first()

            if datos:
            
                datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'link', 'tipo_virtual']
                respuesta = SerializadorUniversal.serializar_unico(dato= datos, campos_requeridos= datos_requeridos)
                return respuesta, respuesta_datos_sesion
            else:
                return None, None
        else:
            return None, None

    #def crear(correo, nombres, apellidos, carnet, telefono, celular_titular, nombres_titular, nombre_nivel, rango_nivel, extension, ocupacion_tutor, parentesco_tutor, numero_cuenta, numero_contrato, inicio_contrato, fin_contrato):
    def crear(correo, nombres, apellidos, carnet, telefono, celular_titular, nombres_titular, nombre_nivel, rango_nivel, extension, ocupacion_tutor, parentesco_tutor, numero_cuenta, numero_contrato, inicio_contrato, fin_contrato, seccion_correspondiente, nivel_correspondiente):

        wel_nvl_corr = 0
        wor_nvl_corr = 0
        ess_nvl_corr = 0
        spk_nvl_corr = 0
        paso_examen = 0

        sec_corr = str(seccion_correspondiente)

        nivel_correspondiente = int(nivel_correspondiente)
        

        if nivel_correspondiente==0:
            wel_nvl_corr = 0
            wor_nvl_corr = 0
            ess_nvl_corr = 0
            spk_nvl_corr = 0
            paso_examen = 0
        elif (nivel_correspondiente%5==0 and sec_corr.startswith('Test')):
            wel_nvl_corr = 1
            wor_nvl_corr = int(nivel_correspondiente)
            ess_nvl_corr = int(nivel_correspondiente)
            spk_nvl_corr = int(nivel_correspondiente)
            paso_examen = 0
        elif (sec_corr=='Essential' and nivel_correspondiente%5==1):
            wel_nvl_corr = 1
            wor_nvl_corr = int(nivel_correspondiente) - 1
            ess_nvl_corr = int(nivel_correspondiente) - 1
            spk_nvl_corr = int(nivel_correspondiente) - 1
            paso_examen = 1
        elif (sec_corr=='Essential'):
            wel_nvl_corr = 1
            wor_nvl_corr = int(nivel_correspondiente) - 1
            ess_nvl_corr = int(nivel_correspondiente) - 1
            spk_nvl_corr = int(nivel_correspondiente) - 1
            paso_examen = 0
        elif (sec_corr=='Working'):
            wel_nvl_corr = 1
            wor_nvl_corr = int(nivel_correspondiente)
            ess_nvl_corr = int(nivel_correspondiente) - 1
            spk_nvl_corr = int(nivel_correspondiente) - 1
            paso_examen = 0
        elif (sec_corr=='Speak Out'):
            wel_nvl_corr = 1
            wor_nvl_corr = int(nivel_correspondiente)
            ess_nvl_corr = int(nivel_correspondiente)
            spk_nvl_corr = int(nivel_correspondiente) - 1
            paso_examen = 0

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


        estudiante = Estudiante(nombre_usuario, str(carnet), correo, nombres, apellidos, carnet, telefono, celular_titular, nombres_titular, nombre_nivel, rango_nivel, extension, ocupacion_tutor, parentesco_tutor, numero_cuenta, numero_contrato, inicio_contrato, fin_contrato)


        db.session.add(estudiante)
        db.session.commit()

        estudiante.welcome_completado = wel_nvl_corr
        estudiante.working_completado = wor_nvl_corr
        estudiante.essential_completado = ess_nvl_corr
        estudiante.speakout_completado = spk_nvl_corr
        estudiante.paso_examen = paso_examen
        db.session.commit()


        repuesta = ServiciosCorreo.enviar_credenciales_nuevo_usuario(correo, nombre_usuario, str(carnet))

        return True
    
    def obtener_todos():

        datos = Estudiante.query.filter_by(activo = 1)

        datos_requeridos = ['id_estudiante', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'celular_titular', 'nombres_titular', 'nombre_nivel', 'rango_nivel', 'speakout_completado', 'working_completado', 'essential_completado', 'welcome_completado', 'activo', 'paso_examen']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)

        if respuesta:
            for resp in respuesta:
                n_working = int(resp['working_completado'])
                n_speakout = int(resp['speakout_completado'])
                n_welcome = int(resp['welcome_completado'])
                n_essential = int(resp['essential_completado'])
                flag_examen = int(resp['paso_examen'])
                seccion_correspondiente = ''
                nivel_correspondiente = ''
                if n_welcome == 0:
                    seccion_correspondiente = 'Welcome'
                    nivel_correspondiente = '0'
                elif (n_essential==n_working and n_working==n_speakout and n_speakout%5==0 and flag_examen==0):
                    nivel_correspondiente = str(n_speakout)
                    sesiones = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, DetalleSesion.id_sesion==Sesion.id_sesion).filter(Sesion.seccion=='Test Escrito', DetalleSesion.nivel_seccion==n_speakout, DetalleSesion.calificacion>=85.0).all()
                    if sesiones:
                        seccion_correspondiente = 'Test Oral'
                    else:
                        seccion_correspondiente = 'Test Escrito'
                elif (n_essential==n_working and n_working==n_speakout and n_speakout%5==0 and flag_examen==1):
                    nivel_correspondiente = str(n_speakout+1)
                    seccion_correspondiente = 'Essential'
                elif (n_essential==n_working and n_working==n_speakout):
                    nivel_correspondiente = str(n_speakout+1)
                    seccion_correspondiente = 'Essential'
                elif (n_working==n_speakout):
                    nivel_correspondiente = str(n_speakout+1)
                    seccion_correspondiente = 'Working'
                elif (n_essential==n_working):
                    nivel_correspondiente = str(n_speakout+1)
                    seccion_correspondiente = 'Speak Out'
                
                resp['nivel_correspondiente'] =nivel_correspondiente
                resp['seccion_correspondiente'] =seccion_correspondiente


        return respuesta
    
    def obtener_por_id(id_estudiante):
        estudiante = Estudiante.query.get(id_estudiante)
        if estudiante:
            datos_requeridos = ['id_estudiante', 'nombres', 'apellidos', 'essential_completado', 

                                'working_completado', 'speakout_completado', 'welcome_completado','carnet_identidad', 'telefono', 'correo', 'nombre_usuario', 'celular_titular', 'nombres_titular']

            respuesta = SerializadorUniversal.serializar_unico(dato=estudiante, campos_requeridos=datos_requeridos)
            return respuesta
        return None
        
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
        elif seccion_s == 'Speak Out':
            nivel_est = int(estudiante_op.speakout_completado)
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

        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'activo', 'tipo_virtual']


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
        flag_domingo = False
        if fecha_actual.strftime("%A") == 'Sunday':
            fecha_actual = fecha_actual - timedelta(days=1)
            flag_domingo = True
        

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
        if flag_domingo:
            hoy = hoy - timedelta(days=1)
        
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

        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'activo', 'link', 'tipo_virtual']


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
            if flag_domingo:
                hora_string = '23:00'
            dia_actual = dias_fechas[fecha_actual.strftime('%Y-%m-%d')]
            return respuesta, sesiones_calendario, hora_string, dia_actual, lunes, sabado
        else:
            hora_string = fecha_actual.strftime('%H:%M')
            dia_actual = dias_fechas[fecha_actual.strftime('%Y-%m-%d')]
            if flag_domingo:
                hora_string = '23:00'
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

        
    def inscribir_a_actividad(id_estudiante, id_actividad):
        try:
            actividad = Actividad.query.get(id_actividad)
            estudiante = Estudiante.query.get(id_estudiante)

            if not actividad or not estudiante:
                return {"status": "error", "message": "Actividad o Estudiante no encontrado"}

                # Verificar si hay cupos disponibles
            if actividad.cupos_disponibles <= 0:
                return {"status": "error", "message": "No hay cupos disponibles"}

                # Crear el registro de la inscripción
            detalle = DetalleActividad(id_actividad=id_actividad, id_estudiante=id_estudiante)
            db.session.add(detalle)
            actividad.cupos_disponibles -= 1  # Restar cupo
            db.session.commit()

            return {"status": "success", "message": "Inscripción exitosa"}

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}



    # ------------------------------------------ ALGUNOS PDF'S --------------------------------

    def obtener_reporte_todos_estudiantes(nombre_usuario):

        margin_left = 1.0 * inch
        margin_right = 1.0 * inch
        margin_top = 5 * inch  # Deja espacio para el carimbo
        margin_bottom = 1 * inch

        estudiantes = Estudiante.query.filter(Estudiante.activo==1).all()

        tabla_estudiantes = [['Id Estudiante', 'Nombres', 'Apellidos', 'Carnet de Identidad']]
        for estudiante in estudiantes:
            fila_tabla = [str(estudiante.id_estudiante), str(estudiante.nombres), str(estudiante.apellidos), str(estudiante.carnet_identidad)]
            tabla_estudiantes.append(fila_tabla)

        buffer = BytesIO()
        #pdf = SimpleDocTemplate(buffer, pagesize=letter)
        pdf = SimpleDocTemplate(buffer, pagesize=letter, 
                            leftMargin=margin_left,
                            rightMargin=margin_right,
                            topMargin=margin_top,
                            bottomMargin=margin_bottom)
        elementos = []

        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('Titulo', fontSize=18, alignment=1, fontName="Helvetica-Bold", underline=True)
        estilo_subtitulo_2 = ParagraphStyle('Subtitulo', fontSize=15, alignment=0)  
        estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=10, alignment=0) 
        estilo_datos = estilos['Normal']



        #logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
        #logo_direccion = os.path.join('var', 'www', 'OkAprendeIngles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 1 * inch, 1 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo)
        # Agregar elementos al PDF
        elementos.append(Spacer(1, 55))
       
        elementos.append(Spacer(1, 20))

        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.5 * inch), height - (0.5 * inch) - imagen_logo.drawHeight)
            titulo_x = width / 2  
            titulo_y = height - (2.0 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x - 120, titulo_y, "Informe de Estudiantes de la plataforma")
            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        #elementos.append(Spacer(1, 20))

        tabla_estudiantes_pdf = Table(tabla_estudiantes)

        estilo_tabla = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                   ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 1), (-1, -1), 12),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        
        tabla_estudiantes_pdf.setStyle(estilo_tabla)

        elementos.append(tabla_estudiantes_pdf)
        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer
        
    def obtener_ok_card_pdf(nombre_usuario, id_estudiante):
        estudiante = Estudiante.query.get(id_estudiante)
        if not estudiante:
            return None
        
        detalles_sesion = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, DetalleSesion.id_sesion==Sesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante).order_by(Sesion.fecha, Sesion.hora).all()

        docentes = Docente.query.all()

        lista_docentes = {}
        for docente in docentes:
            lista_docentes[str(docente.id_docente)] = docente.nombres + " " + docente.apellidos

        

        
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        elementos = []

        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('Titulo', fontSize=18, alignment=1, fontName="Helvetica-Bold", underline=True)
        estilo_subtitulo_2 = ParagraphStyle('Subtitulo', fontSize=15, alignment=0)  
        estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=10, alignment=0) 
        estilo_subtitulo_3 = ParagraphStyle('Subtitulo', fontSize=8, alignment=0) 
        estilo_datos = estilos['Normal']

        cabecera = [Paragraph(f"LESSON", estilo_subtitulo_3), Paragraph(f"SESSION", estilo_subtitulo_3), Paragraph(f"DATE", estilo_subtitulo_3), Paragraph(f"HOUR", estilo_subtitulo_3), Paragraph(f"SKILLS(%)", estilo_subtitulo_3), '', Paragraph(f"SIGNATURE", estilo_subtitulo_3), Paragraph(f"TUTOR", estilo_subtitulo_3)]

        tabla_detalle = Table([cabecera,
                              ['Sin Sesiones', '', '', '', '', '', '', '']])
        
        estilo_tabla = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                   #('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 1), (-1, -1), 12),
                                   ('SPAN', (4, 0), (5, 0)),
                                   ('SPAN', (0, 1), (-1, 1)),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        
        tabla_detalle.setStyle(estilo_tabla)

        SIGLAS = {
            'Welcome': 'W',
            'Working': 'WR',
            'Essential': 'E',
            'Speak Out': 'SP',
            'Test Oral': 'Test',
            'Test Escrito': 'Test',
            'Test Mixto': 'Test'
        }

        if detalles_sesion:
            tabla_aux = [cabecera]
            for sesion, detalle in detalles_sesion:
                nota = 'NO'
                if detalle.estado_registro == 'Falto':
                    nota = 'NO'
                else:
                    nota = str(int(detalle.calificacion))
                fila = [Paragraph(f"{detalle.nivel_seccion}", estilo_subtitulo_3),
                        Paragraph(f"{sesion.seccion}", estilo_subtitulo_3),
                        Paragraph(f"{sesion.fecha.strftime('%d/%m/%Y')}", estilo_subtitulo_3),
                        Paragraph(f"{sesion.hora.strftime('%H:%M')}", estilo_subtitulo_3),
                        Paragraph(f"{SIGLAS[str(sesion.seccion)]}", estilo_subtitulo_3),
                        Paragraph(f"{nota}", estilo_subtitulo_3),
                        Paragraph(f"", estilo_subtitulo_3),
                        Paragraph(f"{lista_docentes[str(sesion.id_docente)]}", estilo_subtitulo_3)]
                tabla_aux.append(fila)
            
            estilo_tabla = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                   #('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 1), (-1, -1), 12),
                                   ('SPAN', (4, 0), (5, 0)),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)])

            tabla_detalle = Table(tabla_aux)
            tabla_detalle.setStyle(estilo_tabla)



        #logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
        #logo_direccion = os.path.join('var', 'www', 'OkAprendeIngles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 1 * inch, 1 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo)
        # Agregar elementos al PDF
        elementos.append(Spacer(1, 55))
       
        elementos.append(Spacer(1, 20))

        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.5 * inch), height - (0.5 * inch) - imagen_logo.drawHeight)
            titulo_x = width / 2  
            titulo_y = height - (1.5 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x - 50, titulo_y, "OK CARD")
            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        elementos.append(Spacer(1, 20))

        tabla_carimbo = Table([[Paragraph(f"FULL NAME: <b>{str(estudiante.nombres).upper()} {str(estudiante.apellidos).upper()}</b>", estilo_subtitulo), '', ''],
                               [Paragraph(f"I.D. NUMBER: <b>{estudiante.carnet_identidad} {estudiante.extension}</b>", estilo_subtitulo), Paragraph(f"REG. DATE: <b>{estudiante.inicio_contrato.strftime('%d/%m/%Y')}</b>", estilo_subtitulo), ''],
                               [Paragraph(f"DATE OF BIRTH: <b>0/0/0</b>", estilo_subtitulo), Paragraph(f"DUE. DATE: <b>{estudiante.fin_contrato.strftime('%d/%m/%Y')}</b>", estilo_subtitulo), ''],
                               [Paragraph(f"OCCUPATION: <b>{str(estudiante.ocupacion_tutor).upper()}</b>", estilo_subtitulo), '', ''],
                               [Paragraph(f"HOME ADDRESS: <b>{estudiante.telefono}</b>", estilo_subtitulo), '', Paragraph(f"INVOICE: <b>{estudiante.numero_cuenta}</b>", estilo_subtitulo)],
                               [Paragraph(f"E-MAIL: <b>{estudiante.correo}</b>", estilo_subtitulo), '', Paragraph(f"REGISTTER: <b>{estudiante.numero_contrato}</b>", estilo_subtitulo)]])
        
        estilo_tabla = TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                   #('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 1), (-1, -1), 12),
                                   ('SPAN', (0, 0), (-1, 0)),
                                   ('SPAN', (1, 1), (-1, 1)),
                                   ('SPAN', (1, 2), (-1, 2)),
                                   ('SPAN', (0, 3), (-1, 3)),
                                   ('SPAN', (0, 4), (1, 4)),
                                   ('SPAN', (0, 5), (1, 5)),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)])


        tabla_carimbo.setStyle(estilo_tabla)

        elementos.append(tabla_carimbo)

        elementos.append(Spacer(1, 20))

        elementos.append(tabla_detalle)






        '''tabla_estudiantes_pdf = Table(tabla_estudiantes)

        estilo_tabla = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                   ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 1), (-1, -1), 12),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        
        tabla_estudiantes_pdf.setStyle(estilo_tabla)

        elementos.append(tabla_estudiantes_pdf)'''
        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer
    
    def obtener_sesiones_disponibles_estudiante_id(id_estudiante):
        estudiante = Estudiante.query.get(id_estudiante)

        nivel_working = int(estudiante.working_completado)
        nivel_essential = int(estudiante.essential_completado)
        nivel_speakout = int(estudiante.speakout_completado)
        nivel_welcome = int(estudiante.welcome_completado)

        paso_examen = int(estudiante.paso_examen)

        if paso_examen==1:
            paso_examen = True
        else:
            paso_examen = False

        seccion_correspondiente = 'Welcome'
        nivel_correspondiente = 0

        if(nivel_working==nivel_essential and nivel_essential == nivel_speakout and nivel_speakout%5==0 and not paso_examen):
            nivel_correspondiente = 0
            seccion_correspondiente = 'Test'
        elif(nivel_working==nivel_essential and nivel_essential == nivel_speakout):
            nivel_correspondiente = nivel_essential + 1
            seccion_correspondiente = 'Essential'
        elif(nivel_working==nivel_speakout):
            nivel_correspondiente = nivel_working + 1
            seccion_correspondiente = 'Working'
        elif(nivel_working==nivel_essential):
            nivel_correspondiente = nivel_speakout + 1
            seccion_correspondiente = 'Speak Out'

        hoy = date.today()

        flag_domingo = False

        # en caso de ser domingo
        if hoy.strftime("%A")=='Sunday':
            hoy = hoy + timedelta(days=1)
            flag_domingo = True
        #fin caso de ser domingo 



        manana = hoy + timedelta(days=1)
        dias_al_lunes = hoy.weekday()

        lunes = hoy - timedelta(days= dias_al_lunes)
        sabado = lunes + timedelta(days=5)
        hoy = hoy + timedelta(minutes=30)

        fecha_hoy = hoy.strftime("%Y-%m-%d")
        hora_hoy = hoy.strftime("%H:%M:%S")
        if hoy.strftime("%A")=='Sunday':
            hora_hoy = "06:00:00"
        
        toda = datetime.now()
        hora_hoy = toda.strftime("%H:%M")

        if flag_domingo:
            hora_hoy = "06:00"
        
        #print(hora_hoy)

        fecha_lunes = lunes.strftime("%Y-%m-%d")

        fecha_manana = manana.strftime("%Y-%m-%d")
        fecha_sabado = sabado.strftime("%Y-%m-%d")

        dias_fechas = {}

        fechas_nombres = {}

        dia_string = lunes.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Lunes'
        fecha_aux = lunes + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Martes'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Miercoles'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Jueves'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Viernes'
        dia_string = sabado.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Sabado'

        dia_string = lunes.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = lunes + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        dia_string = sabado.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}

        f_lunes = lunes.strftime("%Y-%m-%d")
        f_sabado = sabado.strftime("%Y-%m-%d")

        dia_actual = fechas_nombres[hoy.strftime("%Y-%m-%d")]
        if flag_domingo:
            dia_actual = 'Domingo'
        


        detalles_generales = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Inscrito', Sesion.fecha>=fecha_lunes, Sesion.fecha<=fecha_sabado).all()

        if detalles_generales:
            return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
        




        
        
        hoy = date.today()

        flag_domingo = False

        # en caso de ser domingo
        if hoy.strftime("%A")=='Sunday':
            hoy = hoy + timedelta(days=1)
            flag_domingo = True
        #fin caso de ser domingo 



        manana = hoy + timedelta(days=1)
        dias_al_lunes = hoy.weekday()

        lunes = hoy - timedelta(days= dias_al_lunes)
        sabado = lunes + timedelta(days=5)
        hoy = hoy + timedelta(minutes=30)

        fecha_hoy = hoy.strftime("%Y-%m-%d")
        hora_hoy = hoy.strftime("%H:%M:%S")
        if hoy.strftime("%A")=='Sunday':
            hora_hoy = "06:00:00"
        
        toda = datetime.now()
        hora_hoy = toda.strftime("%H:%M")

        if flag_domingo:
            hora_hoy = "06:00"
        
        print(hora_hoy)

        fecha_lunes = lunes.strftime("%Y-%m-%d")

        fecha_manana = manana.strftime("%Y-%m-%d")
        fecha_sabado = sabado.strftime("%Y-%m-%d")

        dias_fechas = {}

        fechas_nombres = {}

        dia_string = lunes.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Lunes'
        fecha_aux = lunes + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Martes'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Miercoles'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Jueves'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Viernes'
        dia_string = sabado.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Sabado'

        '''dia_string = lunes.strftime("%Y-%m-%d")
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
        dias_fechas[dia_string] = 'Sabado'''''

        dia_string = lunes.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = lunes + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        dia_string = sabado.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}

        f_lunes = lunes.strftime("%Y-%m-%d")
        f_sabado = sabado.strftime("%Y-%m-%d")

        dia_actual = fechas_nombres[hoy.strftime("%Y-%m-%d")]
        if flag_domingo:
            dia_actual = 'Domingo'



        estudiante = Estudiante.query.filter(Estudiante.activo==1, Estudiante.id_estudiante==id_estudiante).first()

        if not estudiante:
            return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
        
        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
        
        detalles_generales = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Inscrito', Sesion.fecha>=fecha_lunes, Sesion.fecha<=fecha_sabado).all()

        if detalles_generales:
            for sesion, detalle in detalles_generales:
                dias_fechas[sesion.fecha.strftime("%Y-%m-%d")][sesion.hora.strftime("%H:%M:%S")] = True

        speakout_completado = int(estudiante.speakout_completado)
        working_completado = int(estudiante.working_completado)
        essential_completado = int(estudiante.essential_completado)
        welcome_completado = int(estudiante.welcome_completado)

        paso_examen = int(estudiante.paso_examen)

        if paso_examen==1:
            paso_examen = True
        else:
            paso_examen = False

        suma_secciones = speakout_completado + working_completado + essential_completado

        sesiones_disponibles = []

        if welcome_completado == 0: #ess un estudiante nuevo
            detalles = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Inscrito', Sesion.seccion=='Welcome').all()
            if detalles:
                return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            detalles = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Asistio', Sesion.seccion=='Welcome').all()
            if detalles:
                for sesion, detalle in detalles:
                    if detalle.calificacion < 1:
                        return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            detalles = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Welcome').all()
            
            ids_cancelados = []

            if detalles:
                for sesion, detalle in detalles:
                    ids_cancelados.append(sesion.id_sesion)

            sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Welcome', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
            sesiones_hoy = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Welcome', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()

            if sesiones:
                for sesion in sesiones:
                    datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                    if sesion.id_sesion not in ids_cancelados:
                        respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                        sesiones_disponibles.append(respuesta)
            
            if sesiones_hoy:
                for sesion in sesiones_hoy:
                    datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                    if sesion.id_sesion not in ids_cancelados:
                        respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                        sesiones_disponibles.append(respuesta)
        
        elif suma_secciones!=0 and suma_secciones%3==0 and suma_secciones%5==0 and not paso_examen: # si es test
            test_escrito = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Escrito', DetalleSesion.estado_registro=='Inscrito').all()
            if test_escrito:
                return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            test_oral = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Oral', DetalleSesion.estado_registro=='Inscrito').all()
            if test_oral:
                return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            test_mixto = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Mixto', DetalleSesion.estado_registro=='Inscrito').all()
            if test_mixto:
                return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            test_escrito = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Escrito', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion>=85).all()
            test_mixto = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Mixto', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion>=85).all()
            if test_escrito or test_mixto: # aprobado se muestran tests orales
                sesiones_oral = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Oral', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
                sesiones_hoy_oral = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Oral', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()
                sesiones_mixto = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Mixto', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
                sesiones_hoy_mixto = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Mixto', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()

                detalles_mixto = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Test Mixto').all()
                detalles_oral = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Test Oral').all()
            
                ids_cancelados = []

                if detalles_mixto:
                    for sesion, detalle in detalles_mixto:
                        ids_cancelados.append(sesion.id_sesion)
                if detalles_oral:
                    for sesion, detalle in detalles_oral:
                        ids_cancelados.append(sesion.id_sesion)

                if sesiones_oral:
                    for sesion in sesiones_oral:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)

                if sesiones_mixto:
                    for sesion in sesiones_mixto:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
                
                if sesiones_hoy_oral:
                    for sesion in sesiones_hoy_oral:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
                
                if sesiones_hoy_mixto:
                    for sesion in sesiones_hoy_mixto:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)


            else: #no aprobo entonces se muestran tests excritos

                

                sesiones_oral = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Escrito', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
                sesiones_hoy_oral = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Escrito', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()
                sesiones_mixto = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Mixto', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
                sesiones_hoy_mixto = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Mixto', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()

                detalles_mixto = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Test Mixto').all()
                detalles_oral = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Test Oral').all()
            
                ids_cancelados = []

                if detalles_mixto:
                    for sesion, detalle in detalles_mixto:
                        ids_cancelados.append(sesion.id_sesion)
                if detalles_oral:
                    for sesion, detalle in detalles_oral:
                        ids_cancelados.append(sesion.id_sesion)

                if sesiones_oral:
                    for sesion in sesiones_oral:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)

                if sesiones_mixto:
                    for sesion in sesiones_mixto:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
                
                if sesiones_hoy_oral:
                    for sesion in sesiones_hoy_oral:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
                
                if sesiones_hoy_mixto:
                    for sesion in sesiones_hoy_mixto:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
            
        else: # no tiene examenes entonces es clases normales

            speakout_actual = speakout_completado + 1
            working_actual = working_completado + 1
            essential_actual = essential_completado + 1
            
            sesiones_inscritas_working = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Working', DetalleSesion.estado_registro=='Inscrito').all()
            sesiones_inscritas_essential = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Essential', DetalleSesion.estado_registro=='Inscrito').all()
            sesiones_inscritas_speakout = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Speak Out', DetalleSesion.estado_registro=='Inscrito').all()

            sesiones_cancelados_working = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Working', DetalleSesion.estado_registro=='Cancelado').all()
            sesiones_cancelados_essential = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Essential', DetalleSesion.estado_registro=='Cancelado').all()
            sesiones_cancelados_speakout = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Speak Out', DetalleSesion.estado_registro=='Cancelado').all()

            sesiones_asistidas_working = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Working', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion<1).all()
            sesiones_asistidas_essential = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Essential', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion<1).all()
            sesiones_asistidas_speakout = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Speak Out', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion<1).all()

            ids_cancelados = []

            if sesiones_cancelados_essential:
                for sesion, detalle in sesiones_cancelados_essential:
                    ids_cancelados.append(sesion.id_sesion)
            if sesiones_cancelados_working:
                for sesion, detalle in sesiones_cancelados_working:
                    ids_cancelados.append(sesion.id_sesion)
            if sesiones_cancelados_speakout:
                for sesion, detalle in sesiones_cancelados_speakout:
                    ids_cancelados.append(sesion.id_sesion)
            
            sesiones_working = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Working', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
            sesiones_working_hoy = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Working', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()
            sesiones_essential = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Essential', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
            sesiones_essential_hoy = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Essential', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()
            sesiones_speakout = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Speak Out', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
            sesiones_speakout_hoy = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Speak Out', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()

            if seccion_correspondiente == 'Working':
                working_actual = working_completado + 1
                speakout_actual = working_actual + 1
                essential_actual = working_actual + 1
            elif seccion_correspondiente == 'Essential':
                essential_actual = essential_completado + 1
                working_actual = essential_actual + 1
                speakout_actual = essential_actual + 1
            else:
                speakout_actual = speakout_completado + 1
                essential_actual = speakout_actual + 1
                working_actual = speakout_actual + 1
            
            if working_actual == essential_actual and working_actual == speakout_actual and essential_actual == speakout_actual: # mostrar todas las sesiones
                
                

                if sesiones_inscritas_working or sesiones_asistidas_working:
                    print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                else: # anadir sesiones disponibles no canceladas
                    if sesiones_working:
                        for sesion in sesiones_working:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)
                                
                    if sesiones_working_hoy:
                        for sesion in sesiones_working_hoy:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)

                if sesiones_inscritas_essential or sesiones_asistidas_essential:
                    print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                else: # anadir sesiones disponibles no canceladas
                    if sesiones_essential:
                        for sesion in sesiones_essential:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)
                    if sesiones_essential_hoy:
                        for sesion in sesiones_essential_hoy:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)

                if sesiones_inscritas_speakout or sesiones_asistidas_speakout:
                    print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                else: # anadir sesiones disponibles no canceladas
                    if sesiones_speakout:
                        for sesion in sesiones_speakout:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)
                    if sesiones_speakout_hoy:
                        for sesion in sesiones_speakout_hoy:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)
            else: # mostrar solo las menores
                menor = 52
                if working_actual<menor:
                    menor = working_actual
                if essential_actual<menor:
                    menor = essential_actual
                if speakout_actual<menor:
                    menor = speakout_actual

                if menor == working_actual: #MOSTRAR SESINOES WORKING
                    if sesiones_inscritas_working or sesiones_asistidas_working:
                        print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                    else: # anadir sesiones disponibles no canceladas
                        if sesiones_working:
                            for sesion in sesiones_working:
                                flag = True
                                if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                    if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                        flag = False
                                if sesion.id_sesion not in ids_cancelados and flag:
                                    respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                    sesiones_disponibles.append(respuesta)
                        if sesiones_working_hoy:
                            for sesion in sesiones_working_hoy:
                                flag = True
                                if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                    if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                        flag = False
                                if sesion.id_sesion not in ids_cancelados and flag:
                                    respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                    sesiones_disponibles.append(respuesta)
                if menor == essential_actual: #MOSTRAR SESIONES ESSENTIAL
                    if sesiones_inscritas_essential or sesiones_asistidas_essential:
                        print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                    else: # anadir sesiones disponibles no canceladas
                        if sesiones_essential:
                            for sesion in sesiones_essential:
                                flag = True
                                if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                    if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                        flag = False
                                if sesion.id_sesion not in ids_cancelados and flag:
                                    respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                    sesiones_disponibles.append(respuesta)
                        if sesiones_essential_hoy:
                            for sesion in sesiones_essential_hoy:
                                flag = True
                                if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                    if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                        flag = False
                                if sesion.id_sesion not in ids_cancelados and flag:
                                    respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                    sesiones_disponibles.append(respuesta)
                if menor == speakout_actual: #MOSTRAR SESINOES SPEAK
                    if sesiones_inscritas_speakout or sesiones_asistidas_speakout:
                        print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                    else: # anadir sesiones disponibles no canceladas
                        if sesiones_speakout:
                            for sesion in sesiones_speakout:
                                flag = True
                                if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                    if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                        flag = False
                                if sesion.id_sesion not in ids_cancelados and flag:
                                    respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                    sesiones_disponibles.append(respuesta)
                        if sesiones_speakout_hoy:
                            for sesion in sesiones_speakout_hoy:
                                flag = True
                                if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                    if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                        flag = False
                                if sesion.id_sesion not in ids_cancelados and flag:
                                    respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                    sesiones_disponibles.append(respuesta)

        #aqui se deberia retornar los valores de las sesiones disponibles

        sesiones_calendario = {}

        print(sesiones_disponibles)

        for sesion in sesiones_disponibles:
            if sesion['hora'].strftime("%H:%M") not in sesiones_calendario:
                sesiones_calendario[sesion['hora'].strftime("%H:%M")] = {}
            if sesion['fecha'].strftime("%Y-%m-%d") not in sesiones_calendario[sesion['hora'].strftime("%H:%M")]:
                sesiones_calendario[sesion['hora'].strftime("%H:%M")][sesion['fecha'].strftime("%Y-%m-%d")] = []
            
            sesiones_calendario[sesion['hora'].strftime("%H:%M")][sesion['fecha'].strftime("%Y-%m-%d")].append(sesion)
        
        

        return sesiones_disponibles, sesiones_calendario, hora_hoy, dia_actual, f_lunes, f_sabado
        
        


    def obtener_sesiones_pasadas_estudiante_id(id_estudiante):
        estudiante = Estudiante.query.filter(Estudiante.activo==1, Estudiante.id_estudiante==id_estudiante).first()
        if not estudiante:
            return None
        
        fecha_actual = datetime.now()
        fecha_string = fecha_actual.strftime("%Y-%m-%d")
        sesiones_detalles = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, DetalleSesion.id_sesion==Sesion.id_sesion).filter(DetalleSesion.id_estudiante==id_estudiante, Sesion.fecha<=fecha_string).order_by(Sesion.fecha, Sesion.hora).all()

        if not sesiones_detalles:
            return None
        
        sesiones_pasadas = []


        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'activo', 'tipo_virtual']
        for sesion, detalle in sesiones_detalles:
            dict_sesion = SerializadorUniversal.serializar_unico(sesion, datos_requeridos)
            nivel = int(detalle.nivel_seccion)
            if (sesion.seccion == 'Test Oral' or sesion.seccion=='Test Escrito'):
                nivel = str(nivel-4) + "-" + str(nivel)
            elif(sesion.seccion=='Welcome'):
                nivel = '0'
            else:
                nivel = str(nivel+1)
            
            dict_sesion['nivel'] = nivel
            sesiones_pasadas.append(dict_sesion)
        
        return sesiones_pasadas

    def actualizar(id_estudiante, correo, nombres, apellidos, carnet, telefono, nombres_titular, celular_titular, ocupacion_tutor, seccion_correspondiente, nivel_correspondiente):
        try:

            wel_nvl_corr = 0
            wor_nvl_corr = 0
            ess_nvl_corr = 0
            spk_nvl_corr = 0
            paso_examen = 0

            sec_corr = str(seccion_correspondiente)

            nivel_correspondiente = int(nivel_correspondiente)
            

            if nivel_correspondiente==0:
                wel_nvl_corr = 0
                wor_nvl_corr = 0
                ess_nvl_corr = 0
                spk_nvl_corr = 0
                paso_examen = 0
            elif (nivel_correspondiente%5==0 and sec_corr.startswith('Test')):
                wel_nvl_corr = 1
                wor_nvl_corr = int(nivel_correspondiente)
                ess_nvl_corr = int(nivel_correspondiente)
                spk_nvl_corr = int(nivel_correspondiente)
                paso_examen = 0
            elif (sec_corr=='Essential' and nivel_correspondiente%5==1):
                wel_nvl_corr = 1
                wor_nvl_corr = int(nivel_correspondiente) - 1
                ess_nvl_corr = int(nivel_correspondiente) - 1
                spk_nvl_corr = int(nivel_correspondiente) - 1
                paso_examen = 1
            elif (sec_corr=='Essential'):
                wel_nvl_corr = 1
                wor_nvl_corr = int(nivel_correspondiente) - 1
                ess_nvl_corr = int(nivel_correspondiente) - 1
                spk_nvl_corr = int(nivel_correspondiente) - 1
                paso_examen = 0
            elif (sec_corr=='Working'):
                wel_nvl_corr = 1
                wor_nvl_corr = int(nivel_correspondiente)
                ess_nvl_corr = int(nivel_correspondiente) - 1
                spk_nvl_corr = int(nivel_correspondiente) - 1
                paso_examen = 0
            elif (sec_corr=='Speak Out'):
                wel_nvl_corr = 1
                wor_nvl_corr = int(nivel_correspondiente)
                ess_nvl_corr = int(nivel_correspondiente)
                spk_nvl_corr = int(nivel_correspondiente) - 1
                paso_examen = 0

            estudiante = Estudiante.query.get(id_estudiante)
            
            estudiante.correo = correo
            estudiante.nombres = nombres
            estudiante.apellidos = apellidos
            estudiante.carnet_identidad = carnet
            estudiante.nombres_titular = nombres_titular
            estudiante.telefono = telefono
            estudiante.celular_titular = celular_titular
            estudiante.ocupacion_tutor = ocupacion_tutor
            estudiante.welcome_completado = wel_nvl_corr
            estudiante.working_completado = wor_nvl_corr
            estudiante.essential_completado = ess_nvl_corr
            estudiante.speakout_completado = spk_nvl_corr
            estudiante.paso_examen = paso_examen
            db.session.commit()

            return {"status": "success", "message": "Estudiantes modificados exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}

# ---------------------------------------- NUEVAS FUNCIONES SESIONES -------------------------------------

    def obtener_sesiones_disponibles_por_seccion(nivel, seccion, id_estudiante):
        hoy = date.today()
        manana = hoy + timedelta(days=1)
        dias_al_lunes = hoy.weekday()

        lunes = hoy - timedelta(days= dias_al_lunes)
        sabado = lunes + timedelta(days=5)
        hoy = hoy + timedelta(minutes=30)

        fecha_hoy = hoy.strftime("%Y-%m-%d")
        hora_hoy = hoy.strftime("%H:%M:%S")

        fecha_manana = manana.strftime("%Y-%m-%d")
        fecha_sabado = sabado.strftime("%Y-%m-%d")

        sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.seccion==seccion, Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
        sesiones_hoy = Sesion.query.filter(Sesion.activo==1, Sesion.seccion==seccion, Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()

        ids_sesiones = []

        for sesion in sesiones:
            ids_sesiones.append(sesion.id_sesion)
        for sesion in sesiones_hoy:
            ids_sesiones.append(sesion.id_sesion)

        
        

        sesiones_inscritas = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Inscrito').all()
        sesiones_canceladas = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado').all()
        sesiones_asistidas = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Asistio').all()

        if sesiones_inscritas:
            for sesion in sesiones_inscritas:
                if sesion.id_sesion in ids_sesiones:
                    return []
        
        if sesiones_asistidas:
            for sesion in sesiones_asistidas:
                if sesion.id_sesion in ids_sesiones and sesion.calificacion<1:
                    return []
        
        ids_sesiones_canceladas = []

        if sesiones_canceladas:
            for sesion in sesiones_canceladas:
                if sesion.id_sesion in ids_sesiones:
                    ids_sesiones_canceladas.append(sesion.id_sesion)
        
        lista_sesiones_disponibles = []
        
        for sesion in sesiones:
            nivel_inferior = 0
            nivel_superior = 0

            if sesion.nivel != '0':
                nivel_inferior = str(sesion.nivel).split('-')[0]
                nivel_superior = str(sesion.nivel).split('-')[1]
            
            if sesion.id_sesion not in ids_sesiones_canceladas and nivel_inferior<=nivel and nivel <= nivel_superior:
                lista_sesiones_disponibles.append(sesion)

        for sesion in sesiones_hoy:
            nivel_inferior = 0
            nivel_superior = 0

            if sesion.nivel != '0':
                nivel_inferior = str(sesion.nivel).split('-')[0]
                nivel_superior = str(sesion.nivel).split('-')[1]
            
            if sesion.id_sesion not in ids_sesiones_canceladas and nivel_inferior<=nivel and nivel <= nivel_superior:
                lista_sesiones_disponibles.append(sesion)


        if nivel == 'Welcome':
            print()
        elif str(nivel).startswith('Test'):
            print()
        elif nivel == 'Working':
            print()
        
    def obtener_sesiones_disponibles_2(id_estudiante):
        
        hoy = date.today()

        flag_domingo = False

        # en caso de ser domingo
        if hoy.strftime("%A")=='Sunday':
            hoy = hoy + timedelta(days=1)
            flag_domingo = True
        #fin caso de ser domingo 



        manana = hoy + timedelta(days=1)
        dias_al_lunes = hoy.weekday()

        lunes = hoy - timedelta(days= dias_al_lunes)
        sabado = lunes + timedelta(days=5)
        hoy = hoy + timedelta(minutes=30)

        fecha_hoy = hoy.strftime("%Y-%m-%d")
        hora_hoy = hoy.strftime("%H:%M:%S")
        if hoy.strftime("%A")=='Sunday':
            hora_hoy = "06:00:00"
        
        toda = datetime.now()
        hora_hoy = toda.strftime("%H:%M")

        if flag_domingo:
            hora_hoy = "06:00"
        
        print(hora_hoy)

        fecha_lunes = lunes.strftime("%Y-%m-%d")

        fecha_manana = manana.strftime("%Y-%m-%d")
        fecha_sabado = sabado.strftime("%Y-%m-%d")

        dias_fechas = {}

        fechas_nombres = {}

        dia_string = lunes.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Lunes'
        fecha_aux = lunes + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Martes'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Miercoles'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Jueves'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Viernes'
        dia_string = sabado.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Sabado'

        '''dia_string = lunes.strftime("%Y-%m-%d")
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
        dias_fechas[dia_string] = 'Sabado'''''

        dia_string = lunes.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = lunes + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        dia_string = sabado.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}

        f_lunes = lunes.strftime("%Y-%m-%d")
        f_sabado = sabado.strftime("%Y-%m-%d")

        dia_actual = fechas_nombres[hoy.strftime("%Y-%m-%d")]
        if flag_domingo:
            dia_actual = 'Domingo'



        estudiante = Estudiante.query.filter(Estudiante.activo==1, Estudiante.id_estudiante==id_estudiante).first()

        if not estudiante:
            return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
        
        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
        
        detalles_generales = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Inscrito', Sesion.fecha>=fecha_lunes, Sesion.fecha<=fecha_sabado).all()

        if detalles_generales:
            for sesion, detalle in detalles_generales:
                dias_fechas[sesion.fecha.strftime("%Y-%m-%d")][sesion.hora.strftime("%H:%M:%S")] = True

        speakout_completado = int(estudiante.speakout_completado)
        working_completado = int(estudiante.working_completado)
        essential_completado = int(estudiante.essential_completado)
        welcome_completado = int(estudiante.welcome_completado)

        paso_examen = int(estudiante.paso_examen)

        if paso_examen==1:
            paso_examen = True
        else:
            paso_examen = False

        suma_secciones = speakout_completado + working_completado + essential_completado

        sesiones_disponibles = []

        if welcome_completado == 0: #ess un estudiante nuevo
            detalles = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Inscrito', Sesion.seccion=='Welcome').all()
            if detalles:
                return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            detalles = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Asistio', Sesion.seccion=='Welcome').all()
            if detalles:
                for sesion, detalle in detalles:
                    if detalle.calificacion < 1:
                        return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            detalles = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Welcome').all()
            
            ids_cancelados = []

            if detalles:
                for sesion, detalle in detalles:
                    ids_cancelados.append(sesion.id_sesion)

            sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Welcome', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
            sesiones_hoy = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Welcome', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()

            if sesiones:
                for sesion in sesiones:
                    datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                    if sesion.id_sesion not in ids_cancelados:
                        respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                        sesiones_disponibles.append(respuesta)
            
            if sesiones_hoy:
                for sesion in sesiones_hoy:
                    datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                    if sesion.id_sesion not in ids_cancelados:
                        respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                        sesiones_disponibles.append(respuesta)
        
        elif suma_secciones!=0 and suma_secciones%3==0 and suma_secciones%5==0 and not paso_examen: # si es test
            test_escrito = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Escrito', DetalleSesion.estado_registro=='Inscrito').all()
            if test_escrito:
                return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            test_oral = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Oral', DetalleSesion.estado_registro=='Inscrito').all()
            if test_oral:
                return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            test_mixto = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Mixto', DetalleSesion.estado_registro=='Inscrito').all()
            if test_mixto:
                return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            test_escrito = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Escrito', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion>=85).all()
            test_mixto = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Mixto', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion>=85).all()
            if test_escrito or test_mixto: # aprobado se muestran tests orales
                sesiones_oral = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Oral', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
                sesiones_hoy_oral = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Oral', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()
                sesiones_mixto = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Mixto', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
                sesiones_hoy_mixto = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Mixto', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()

                detalles_mixto = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Test Mixto').all()
                detalles_oral = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Test Oral').all()
            
                ids_cancelados = []

                if detalles_mixto:
                    for sesion, detalle in detalles_mixto:
                        ids_cancelados.append(sesion.id_sesion)
                if detalles_oral:
                    for sesion, detalle in detalles_oral:
                        ids_cancelados.append(sesion.id_sesion)

                if sesiones_oral:
                    for sesion in sesiones_oral:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)

                if sesiones_mixto:
                    for sesion in sesiones_mixto:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
                
                if sesiones_hoy_oral:
                    for sesion in sesiones_hoy_oral:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
                
                if sesiones_hoy_mixto:
                    for sesion in sesiones_hoy_mixto:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)


            else: #no aprobo entonces se muestran tests excritos

                

                sesiones_oral = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Escrito', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
                sesiones_hoy_oral = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Escrito', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()
                sesiones_mixto = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Mixto', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
                sesiones_hoy_mixto = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Mixto', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()

                detalles_mixto = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Test Mixto').all()
                detalles_oral = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Test Oral').all()
            
                ids_cancelados = []

                if detalles_mixto:
                    for sesion, detalle in detalles_mixto:
                        ids_cancelados.append(sesion.id_sesion)
                if detalles_oral:
                    for sesion, detalle in detalles_oral:
                        ids_cancelados.append(sesion.id_sesion)

                if sesiones_oral:
                    for sesion in sesiones_oral:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)

                if sesiones_mixto:
                    for sesion in sesiones_mixto:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
                
                if sesiones_hoy_oral:
                    for sesion in sesiones_hoy_oral:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
                
                if sesiones_hoy_mixto:
                    for sesion in sesiones_hoy_mixto:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
            
        else: # no tiene examenes entonces es clases normales

            speakout_actual = speakout_completado + 1
            working_actual = working_completado + 1
            essential_actual = essential_completado + 1
            
            sesiones_inscritas_working = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Working', DetalleSesion.estado_registro=='Inscrito').all()
            sesiones_inscritas_essential = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Essential', DetalleSesion.estado_registro=='Inscrito').all()
            sesiones_inscritas_speakout = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Speak Out', DetalleSesion.estado_registro=='Inscrito').all()

            sesiones_cancelados_working = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Working', DetalleSesion.estado_registro=='Cancelado').all()
            sesiones_cancelados_essential = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Essential', DetalleSesion.estado_registro=='Cancelado').all()
            sesiones_cancelados_speakout = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Speak Out', DetalleSesion.estado_registro=='Cancelado').all()

            sesiones_asistidas_working = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Working', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion<1).all()
            sesiones_asistidas_essential = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Essential', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion<1).all()
            sesiones_asistidas_speakout = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Speak Out', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion<1).all()

            ids_cancelados = []

            if sesiones_cancelados_essential:
                for sesion, detalle in sesiones_cancelados_essential:
                    ids_cancelados.append(sesion.id_sesion)
            if sesiones_cancelados_working:
                for sesion, detalle in sesiones_cancelados_working:
                    ids_cancelados.append(sesion.id_sesion)
            if sesiones_cancelados_speakout:
                for sesion, detalle in sesiones_cancelados_speakout:
                    ids_cancelados.append(sesion.id_sesion)
            
            sesiones_working = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Working', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
            sesiones_working_hoy = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Working', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()
            sesiones_essential = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Essential', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
            sesiones_essential_hoy = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Essential', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()
            sesiones_speakout = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Speak Out', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
            sesiones_speakout_hoy = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Speak Out', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()
            
            if working_actual == essential_actual and working_actual == speakout_actual and essential_actual == speakout_actual: # mostrar todas las sesiones
                
                

                if sesiones_inscritas_working or sesiones_asistidas_working:
                    print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                else: # anadir sesiones disponibles no canceladas
                    if sesiones_working:
                        for sesion in sesiones_working:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)
                                
                    if sesiones_working_hoy:
                        for sesion in sesiones_working_hoy:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)

                if sesiones_inscritas_essential or sesiones_asistidas_essential:
                    print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                else: # anadir sesiones disponibles no canceladas
                    if sesiones_essential:
                        for sesion in sesiones_essential:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)
                    if sesiones_essential_hoy:
                        for sesion in sesiones_essential_hoy:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)

                if sesiones_inscritas_speakout or sesiones_asistidas_speakout:
                    print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                else: # anadir sesiones disponibles no canceladas
                    if sesiones_speakout:
                        for sesion in sesiones_speakout:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)
                    if sesiones_speakout_hoy:
                        for sesion in sesiones_speakout_hoy:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)
            else: # mostrar solo las menores
                menor = 52
                if working_actual<menor:
                    menor = working_actual
                if essential_actual<menor:
                    menor = essential_actual
                if speakout_actual<menor:
                    menor = speakout_actual

                if menor == working_actual: #MOSTRAR SESINOES WORKING
                    if sesiones_inscritas_working or sesiones_asistidas_working:
                        print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                    else: # anadir sesiones disponibles no canceladas
                        if sesiones_working:
                            for sesion in sesiones_working:
                                flag = True
                                if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                    if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                        flag = False
                                if sesion.id_sesion not in ids_cancelados and flag:
                                    respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                    sesiones_disponibles.append(respuesta)
                        if sesiones_working_hoy:
                            for sesion in sesiones_working_hoy:
                                flag = True
                                if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                    if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                        flag = False
                                if sesion.id_sesion not in ids_cancelados and flag:
                                    respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                    sesiones_disponibles.append(respuesta)
                if menor == essential_actual: #MOSTRAR SESIONES ESSENTIAL
                    if sesiones_inscritas_essential or sesiones_asistidas_essential:
                        print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                    else: # anadir sesiones disponibles no canceladas
                        if sesiones_essential:
                            for sesion in sesiones_essential:
                                flag = True
                                if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                    if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                        flag = False
                                if sesion.id_sesion not in ids_cancelados and flag:
                                    respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                    sesiones_disponibles.append(respuesta)
                        if sesiones_essential_hoy:
                            for sesion in sesiones_essential_hoy:
                                flag = True
                                if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                    if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                        flag = False
                                if sesion.id_sesion not in ids_cancelados and flag:
                                    respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                    sesiones_disponibles.append(respuesta)
                if menor == speakout_actual: #MOSTRAR SESINOES SPEAK
                    if sesiones_inscritas_speakout or sesiones_asistidas_speakout:
                        print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                    else: # anadir sesiones disponibles no canceladas
                        if sesiones_speakout:
                            for sesion in sesiones_speakout:
                                flag = True
                                if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                    if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                        flag = False
                                if sesion.id_sesion not in ids_cancelados and flag:
                                    respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                    sesiones_disponibles.append(respuesta)
                        if sesiones_speakout_hoy:
                            for sesion in sesiones_speakout_hoy:
                                flag = True
                                if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                    if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                        flag = False
                                if sesion.id_sesion not in ids_cancelados and flag:
                                    respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                    sesiones_disponibles.append(respuesta)

        #aqui se deberia retornar los valores de las sesiones disponibles

        sesiones_calendario = {}

        print(sesiones_disponibles)

        for sesion in sesiones_disponibles:
            if sesion['hora'].strftime("%H:%M") not in sesiones_calendario:
                sesiones_calendario[sesion['hora'].strftime("%H:%M")] = {}
            if sesion['fecha'].strftime("%Y-%m-%d") not in sesiones_calendario[sesion['hora'].strftime("%H:%M")]:
                sesiones_calendario[sesion['hora'].strftime("%H:%M")][sesion['fecha'].strftime("%Y-%m-%d")] = []
            
            sesiones_calendario[sesion['hora'].strftime("%H:%M")][sesion['fecha'].strftime("%Y-%m-%d")].append(sesion)
        
        

        return sesiones_disponibles, sesiones_calendario, hora_hoy, dia_actual, f_lunes, f_sabado
            
            

    

    # ------------------------------------------ ALGUNOS PDF'S --------------------------------

    def obtener_reporte_todos_estudiantes(nombre_usuario):

        margin_left = 0.5 * inch
        margin_right = 0.5 * inch
        margin_top = 2.2 * inch  # Deja espacio para el carimbo
        margin_bottom = 1 * inch

        estudiantes = Estudiante.query.filter(Estudiante.activo==1).all()

        

        buffer = BytesIO()
        #pdf = SimpleDocTemplate(buffer, pagesize=letter)
        pdf = SimpleDocTemplate(buffer, pagesize=letter, 
                            leftMargin=margin_left,
                            rightMargin=margin_right,
                            topMargin=margin_top,
                            bottomMargin=margin_bottom)
        elementos = []

        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('Titulo', fontSize=18, alignment=1, fontName="Helvetica-Bold", underline=True)
        estilo_subtitulo_2 = ParagraphStyle('Subtitulo', fontSize=12, alignment=1, fontName="Helvetica-Bold")  
        estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=10, alignment=0) 
        estilo_datos = ParagraphStyle('datos_tabla', fontSize=10, alignment=0)



        #logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
        #logo_direccion = os.path.join('var', 'www', 'OkAprendeIngles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 1 * inch, 1 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo)
        # Agregar elementos al PDF
        #elementos.append(Spacer(1, 55))
       
        #elementos.append(Spacer(1, 20))

        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.5 * inch), height - (0.5 * inch) - imagen_logo.drawHeight)
            titulo_x = width / 2  
            titulo_y = height - (2.0 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x - 120, titulo_y, "Informe de Estudiantes de la plataforma")
            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        #elementos.append(Spacer(1, 20))

        tabla_estudiantes = [[
            Paragraph('Id', estilo_subtitulo_2),
            Paragraph('Nombres', estilo_subtitulo_2),
            Paragraph('Apellidos', estilo_subtitulo_2),
            Paragraph('Carnet de Identidad', estilo_subtitulo_2),
            Paragraph('Fecha de Inicio de Contrato', estilo_subtitulo_2),
            Paragraph('Fecha de Finalizacion de Contrato', estilo_subtitulo_2)]
            ]
        for estudiante in estudiantes:
            fila_tabla = [
                Paragraph(f'{str(estudiante.id_estudiante)}', estilo_datos),
                Paragraph(f'{str(estudiante.nombres)}', estilo_datos),
                Paragraph(f'{str(estudiante.apellidos)}', estilo_datos),
                Paragraph(f'{str(estudiante.carnet_identidad)}', estilo_datos),
                Paragraph(f'{estudiante.inicio_contrato.strftime("%d-%m-%Y")}', estilo_datos),
                Paragraph(f'{estudiante.fin_contrato.strftime("%d-%m-%Y")}', estilo_datos)]
            tabla_estudiantes.append(fila_tabla)
        tamano_columnas = [0.8 * inch, 1.0 * inch, 1.0 * inch, 1.1 * inch, 1.1 * inch, 1.3 * inch]

        tabla_estudiantes_pdf = Table(tabla_estudiantes, colWidths=tamano_columnas)

        estilo_tabla = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                   ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 1), (-1, -1), 10),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        
        tabla_estudiantes_pdf.setStyle(estilo_tabla)

        elementos.append(tabla_estudiantes_pdf)
        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer


    def obtener_ok_card_pdf(nombre_usuario, id_estudiante):
        margin_left = 1.0 * inch
        margin_right = 1.0 * inch
        margin_top = 1.8 * inch  # Deja espacio para el carimbo
        margin_bottom = 1 * inch

        estudiante = Estudiante.query.get(id_estudiante)
        if not estudiante:
            return None
        
        detalles_sesion = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, DetalleSesion.id_sesion==Sesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante).order_by(Sesion.fecha, Sesion.hora).all()

        docentes = Docente.query.all()

        lista_docentes = {}
        for docente in docentes:
            lista_docentes[str(docente.id_docente)] = docente.nombres + " " + docente.apellidos

        

        
        buffer = BytesIO()
        #pdf = SimpleDocTemplate(buffer, pagesize=letter)
        pdf = SimpleDocTemplate(buffer, pagesize=letter, 
                            leftMargin=margin_left,
                            rightMargin=margin_right,
                            topMargin=margin_top,
                            bottomMargin=margin_bottom)
        elementos = []

        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('Titulo', fontSize=18, alignment=1, fontName="Helvetica-Bold", underline=True)
        estilo_subtitulo_2 = ParagraphStyle('Subtitulo', fontSize=15, alignment=0)  
        estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=10, alignment=0) 
        estilo_subtitulo_3 = ParagraphStyle('Subtitulo', fontSize=8, alignment=0) 
        estilo_datos = estilos['Normal']

        cabecera = [Paragraph(f"LESSON", estilo_subtitulo_3), Paragraph(f"SESSION", estilo_subtitulo_3), Paragraph(f"DATE", estilo_subtitulo_3), Paragraph(f"HOUR", estilo_subtitulo_3), Paragraph(f"SKILLS(%)", estilo_subtitulo_3), '', Paragraph(f"SIGNATURE", estilo_subtitulo_3), Paragraph(f"TUTOR", estilo_subtitulo_3)]

        tabla_detalle = Table([cabecera,
                              ['Sin Sesiones', '', '', '', '', '', '', '']])
        
        estilo_tabla = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                   #('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 1), (-1, -1), 12),
                                   ('SPAN', (4, 0), (5, 0)),
                                   ('SPAN', (0, 1), (-1, 1)),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        
        tabla_detalle.setStyle(estilo_tabla)

        SIGLAS = {
            'Welcome': 'W',
            'Working': 'WR',
            'Essential': 'E',
            'Speak Out': 'SP',
            'Test Oral': 'Test',
            'Test Escrito': 'Test',
            'Test Mixto': 'Test',
            'Test': 'Test'
        }

        if detalles_sesion:
            tabla_aux = [cabecera]
            for sesion, detalle in detalles_sesion:
                nota = 'NO'
                if detalle.estado_registro == 'Falto':
                    nota = 'Falto'
                elif detalle.estado_registro == 'Cancelado':
                    nota = 'Cancelo'
                else:
                    nota = str(int(detalle.calificacion))
                fila = [Paragraph(f"{detalle.nivel_seccion+1}", estilo_subtitulo_3),
                        Paragraph(f"{sesion.seccion}", estilo_subtitulo_3),
                        Paragraph(f"{sesion.fecha.strftime('%d/%m/%Y')}", estilo_subtitulo_3),
                        Paragraph(f"{sesion.hora.strftime('%H:%M')}", estilo_subtitulo_3),
                        Paragraph(f"{SIGLAS[str(sesion.seccion)]}", estilo_subtitulo_3),
                        Paragraph(f"{nota}", estilo_subtitulo_3),
                        Paragraph(f"", estilo_subtitulo_3),
                        Paragraph(f"{lista_docentes[str(sesion.id_docente)]}", estilo_subtitulo_3)]
                tabla_aux.append(fila)
            
            estilo_tabla = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                   #('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 1), (-1, -1), 12),
                                   ('SPAN', (4, 0), (5, 0)),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)])

            tabla_detalle = Table(tabla_aux)
            tabla_detalle.setStyle(estilo_tabla)



        #logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
        #logo_direccion = os.path.join('var', 'www', 'OkAprendeIngles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 1 * inch, 1 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo)
        # Agregar elementos al PDF
        #elementos.append(Spacer(1, 55))
       
        #elementos.append(Spacer(1, 20))

        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.5 * inch), height - (0.5 * inch) - imagen_logo.drawHeight)
            titulo_x = width / 2  
            titulo_y = height - (1.5 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x - 50, titulo_y, "OK CARD")
            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        #elementos.append(Spacer(1, 20))

        tabla_carimbo = Table([[Paragraph(f"FULL NAME: <b>{str(estudiante.nombres).upper()} {str(estudiante.apellidos).upper()}</b>", estilo_subtitulo), '', ''],
                               [Paragraph(f"I.D. NUMBER: <b>{estudiante.carnet_identidad} {estudiante.extension}</b>", estilo_subtitulo), Paragraph(f"REG. DATE: <b>{estudiante.inicio_contrato.strftime('%d/%m/%Y')}</b>", estilo_subtitulo), ''],
                               [Paragraph(f"DATE OF BIRTH: <b>0/0/0</b>", estilo_subtitulo), Paragraph(f"DUE. DATE: <b>{estudiante.fin_contrato.strftime('%d/%m/%Y')}</b>", estilo_subtitulo), ''],
                               [Paragraph(f"OCCUPATION: <b>{str(estudiante.ocupacion_tutor).upper()}</b>", estilo_subtitulo), '', ''],
                               [Paragraph(f"HOME ADDRESS: <b>{estudiante.telefono}</b>", estilo_subtitulo), '', Paragraph(f"INVOICE: <b>{estudiante.numero_cuenta}</b>", estilo_subtitulo)],
                               [Paragraph(f"E-MAIL: <b>{estudiante.correo}</b>", estilo_subtitulo), '', Paragraph(f"REGISTTER: <b>{estudiante.numero_contrato}</b>", estilo_subtitulo)]])
        
        estilo_tabla = TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                   #('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 1), (-1, -1), 12),
                                   ('SPAN', (0, 0), (-1, 0)),
                                   ('SPAN', (1, 1), (-1, 1)),
                                   ('SPAN', (1, 2), (-1, 2)),
                                   ('SPAN', (0, 3), (-1, 3)),
                                   ('SPAN', (0, 4), (1, 4)),
                                   ('SPAN', (0, 5), (1, 5)),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)])


        tabla_carimbo.setStyle(estilo_tabla)

        elementos.append(tabla_carimbo)

        elementos.append(Spacer(1, 20))

        elementos.append(tabla_detalle)






        '''tabla_estudiantes_pdf = Table(tabla_estudiantes)

        estilo_tabla = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                   ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 1), (-1, -1), 12),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        
        tabla_estudiantes_pdf.setStyle(estilo_tabla)

        elementos.append(tabla_estudiantes_pdf)'''
        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer
    
    def obtener_sesiones_disponibles_estudiante_id_2(id_estudiante):
        estudiante = Estudiante.query.get(id_estudiante)

        nivel_working = int(estudiante.working_completado)
        nivel_essential = int(estudiante.essential_completado)
        nivel_speakout = int(estudiante.speakout_completado)
        nivel_welcome = int(estudiante.welcome_completado)

        paso_examen = int(estudiante.paso_examen)

        if paso_examen==1:
            paso_examen = True
        else:
            paso_examen = False

        seccion_correspondiente = 'Welcome'
        nivel_correspondiente = 0

        if(nivel_working==nivel_essential and nivel_essential == nivel_speakout and nivel_speakout%5==0 and not paso_examen):
            nivel_correspondiente = 0
            seccion_correspondiente = 'Test'
        elif(nivel_working==nivel_essential and nivel_essential == nivel_speakout):
            nivel_correspondiente = nivel_essential + 1
            seccion_correspondiente = 'Essential'
        elif(nivel_working==nivel_speakout):
            nivel_correspondiente = nivel_working + 1
            seccion_correspondiente = 'Working'
        elif(nivel_working==nivel_essential):
            nivel_correspondiente = nivel_speakout + 1
            seccion_correspondiente = 'Speak Out'

        hoy = date.today()

        flag_domingo = False

        # en caso de ser domingo
        if hoy.strftime("%A")=='Sunday':
            hoy = hoy + timedelta(days=1)
            flag_domingo = True
        #fin caso de ser domingo 



        manana = hoy + timedelta(days=1)
        dias_al_lunes = hoy.weekday()

        lunes = hoy - timedelta(days= dias_al_lunes)
        sabado = lunes + timedelta(days=5)
        hoy = hoy + timedelta(minutes=30)

        fecha_hoy = hoy.strftime("%Y-%m-%d")
        hora_hoy = hoy.strftime("%H:%M:%S")
        if hoy.strftime("%A")=='Sunday':
            hora_hoy = "06:00:00"
        
        toda = datetime.now()
        hora_hoy = toda.strftime("%H:%M")

        if flag_domingo:
            hora_hoy = "06:00"
        
        #print(hora_hoy)

        fecha_lunes = lunes.strftime("%Y-%m-%d")

        fecha_manana = manana.strftime("%Y-%m-%d")
        fecha_sabado = sabado.strftime("%Y-%m-%d")

        dias_fechas = {}

        fechas_nombres = {}

        dia_string = lunes.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Lunes'
        fecha_aux = lunes + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Martes'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Miercoles'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Jueves'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Viernes'
        dia_string = sabado.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Sabado'

        dia_string = lunes.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = lunes + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        dia_string = sabado.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}

        f_lunes = lunes.strftime("%Y-%m-%d")
        f_sabado = sabado.strftime("%Y-%m-%d")

        dia_actual = fechas_nombres[hoy.strftime("%Y-%m-%d")]
        if flag_domingo:
            dia_actual = 'Domingo'
        


        detalles_generales = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Inscrito', Sesion.fecha>=fecha_lunes, Sesion.fecha<=fecha_sabado).all()

        if detalles_generales:
            return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
        




        
        
        hoy = date.today()

        flag_domingo = False

        # en caso de ser domingo
        if hoy.strftime("%A")=='Sunday':
            hoy = hoy + timedelta(days=1)
            flag_domingo = True
        #fin caso de ser domingo 



        manana = hoy + timedelta(days=1)
        dias_al_lunes = hoy.weekday()

        lunes = hoy - timedelta(days= dias_al_lunes)
        sabado = lunes + timedelta(days=5)
        hoy = hoy + timedelta(minutes=30)

        fecha_hoy = hoy.strftime("%Y-%m-%d")
        hora_hoy = hoy.strftime("%H:%M:%S")
        if hoy.strftime("%A")=='Sunday':
            hora_hoy = "06:00:00"
        
        toda = datetime.now()
        hora_hoy = toda.strftime("%H:%M")

        if flag_domingo:
            hora_hoy = "06:00"
        
        print(hora_hoy)

        fecha_lunes = lunes.strftime("%Y-%m-%d")

        fecha_manana = manana.strftime("%Y-%m-%d")
        fecha_sabado = sabado.strftime("%Y-%m-%d")

        dias_fechas = {}

        fechas_nombres = {}

        dia_string = lunes.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Lunes'
        fecha_aux = lunes + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Martes'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Miercoles'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Jueves'
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Viernes'
        dia_string = sabado.strftime("%Y-%m-%d")
        fechas_nombres[dia_string] = 'Sabado'

        '''dia_string = lunes.strftime("%Y-%m-%d")
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
        dias_fechas[dia_string] = 'Sabado'''''

        dia_string = lunes.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = lunes + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        fecha_aux = fecha_aux + timedelta(days=1)
        dia_string = fecha_aux.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}
        dia_string = sabado.strftime("%Y-%m-%d")
        dias_fechas[dia_string] = {}

        f_lunes = lunes.strftime("%Y-%m-%d")
        f_sabado = sabado.strftime("%Y-%m-%d")

        dia_actual = fechas_nombres[hoy.strftime("%Y-%m-%d")]
        if flag_domingo:
            dia_actual = 'Domingo'



        estudiante = Estudiante.query.filter(Estudiante.activo==1, Estudiante.id_estudiante==id_estudiante).first()

        if not estudiante:
            return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
        
        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
        
        detalles_generales = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Inscrito', Sesion.fecha>=fecha_lunes, Sesion.fecha<=fecha_sabado).all()

        if detalles_generales:
            for sesion, detalle in detalles_generales:
                dias_fechas[sesion.fecha.strftime("%Y-%m-%d")][sesion.hora.strftime("%H:%M:%S")] = True

        speakout_completado = int(estudiante.speakout_completado)
        working_completado = int(estudiante.working_completado)
        essential_completado = int(estudiante.essential_completado)
        welcome_completado = int(estudiante.welcome_completado)

        paso_examen = int(estudiante.paso_examen)

        if paso_examen==1:
            paso_examen = True
        else:
            paso_examen = False

        suma_secciones = speakout_completado + working_completado + essential_completado

        sesiones_disponibles = []

        if welcome_completado == 0: #ess un estudiante nuevo
            detalles = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Inscrito', Sesion.seccion=='Welcome').all()
            if detalles:
                return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            detalles = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Asistio', Sesion.seccion=='Welcome').all()
            if detalles:
                for sesion, detalle in detalles:
                    if detalle.calificacion < 1:
                        return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            detalles = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Welcome').all()
            
            ids_cancelados = []

            if detalles:
                for sesion, detalle in detalles:
                    ids_cancelados.append(sesion.id_sesion)

            sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Welcome', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
            sesiones_hoy = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Welcome', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()

            if sesiones:
                for sesion in sesiones:
                    datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                    if sesion.id_sesion not in ids_cancelados:
                        respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                        sesiones_disponibles.append(respuesta)
            
            if sesiones_hoy:
                for sesion in sesiones_hoy:
                    datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                    if sesion.id_sesion not in ids_cancelados:
                        respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                        sesiones_disponibles.append(respuesta)
        
        elif suma_secciones!=0 and suma_secciones%3==0 and suma_secciones%5==0 and not paso_examen and speakout_completado!=45 and speakout_completado!=35: # si es test
            test_escrito = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Escrito', DetalleSesion.estado_registro=='Inscrito').all()
            if test_escrito:
                return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            test_oral = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Oral', DetalleSesion.estado_registro=='Inscrito').all()
            if test_oral:
                return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            test_mixto = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Mixto', DetalleSesion.estado_registro=='Inscrito').all()
            if test_mixto:
                return [], [], hora_hoy, dia_actual, f_lunes, f_sabado
            
            test_escrito = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Escrito', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion>=85).all()
            test_mixto = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Test Mixto', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion>=85).all()
            if test_escrito or test_mixto: # aprobado se muestran tests orales
                sesiones_oral = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Oral', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
                sesiones_hoy_oral = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Oral', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()
                sesiones_mixto = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Mixto', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
                sesiones_hoy_mixto = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Mixto', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()

                detalles_mixto = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Test Mixto').all()
                detalles_oral = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Test Oral').all()
            
                ids_cancelados = []

                if detalles_mixto:
                    for sesion, detalle in detalles_mixto:
                        ids_cancelados.append(sesion.id_sesion)
                if detalles_oral:
                    for sesion, detalle in detalles_oral:
                        ids_cancelados.append(sesion.id_sesion)

                if sesiones_oral:
                    for sesion in sesiones_oral:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)

                if sesiones_mixto:
                    for sesion in sesiones_mixto:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
                
                if sesiones_hoy_oral:
                    for sesion in sesiones_hoy_oral:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
                
                if sesiones_hoy_mixto:
                    for sesion in sesiones_hoy_mixto:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)


            else: #no aprobo entonces se muestran tests excritos

                

                sesiones_oral = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Escrito', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
                sesiones_hoy_oral = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Escrito', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()
                sesiones_mixto = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Mixto', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
                sesiones_hoy_mixto = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Test Mixto', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()

                detalles_mixto = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Test Mixto').all()
                detalles_oral = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, DetalleSesion.estado_registro=='Cancelado', Sesion.seccion=='Test Oral').all()
            
                ids_cancelados = []

                if detalles_mixto:
                    for sesion, detalle in detalles_mixto:
                        ids_cancelados.append(sesion.id_sesion)
                if detalles_oral:
                    for sesion, detalle in detalles_oral:
                        ids_cancelados.append(sesion.id_sesion)

                if sesiones_oral:
                    for sesion in sesiones_oral:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)

                if sesiones_mixto:
                    for sesion in sesiones_mixto:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
                
                if sesiones_hoy_oral:
                    for sesion in sesiones_hoy_oral:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
                
                if sesiones_hoy_mixto:
                    for sesion in sesiones_hoy_mixto:
                        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'cupos_disponibles', 'link', 'imagen_url', 'activo', 'tipo_virtual']
                        if sesion.id_sesion not in ids_cancelados:
                            respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                            sesiones_disponibles.append(respuesta)
            
        else: # no tiene examenes entonces es clases normales

            speakout_actual = speakout_completado + 1
            working_actual = working_completado + 1
            essential_actual = essential_completado + 1
            
            sesiones_inscritas_working = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Working', DetalleSesion.estado_registro=='Inscrito').all()
            sesiones_inscritas_essential = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Essential', DetalleSesion.estado_registro=='Inscrito').all()
            sesiones_inscritas_speakout = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Speak Out', DetalleSesion.estado_registro=='Inscrito').all()

            sesiones_cancelados_working = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Working', DetalleSesion.estado_registro=='Cancelado').all()
            sesiones_cancelados_essential = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Essential', DetalleSesion.estado_registro=='Cancelado').all()
            sesiones_cancelados_speakout = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Speak Out', DetalleSesion.estado_registro=='Cancelado').all()

            sesiones_asistidas_working = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Working', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion<1).all()
            sesiones_asistidas_essential = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Essential', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion<1).all()
            sesiones_asistidas_speakout = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, Sesion.id_sesion==DetalleSesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.activo==1, DetalleSesion.id_estudiante==id_estudiante, Sesion.seccion=='Speak Out', DetalleSesion.estado_registro=='Asistio', DetalleSesion.calificacion<1).all()

            ids_cancelados = []

            if sesiones_cancelados_essential:
                for sesion, detalle in sesiones_cancelados_essential:
                    ids_cancelados.append(sesion.id_sesion)
            if sesiones_cancelados_working:
                for sesion, detalle in sesiones_cancelados_working:
                    ids_cancelados.append(sesion.id_sesion)
            if sesiones_cancelados_speakout:
                for sesion, detalle in sesiones_cancelados_speakout:
                    ids_cancelados.append(sesion.id_sesion)
            
            sesiones_working = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Working', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
            sesiones_working_hoy = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Working', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()
            sesiones_essential = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Essential', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
            sesiones_essential_hoy = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Essential', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()
            sesiones_speakout = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Speak Out', Sesion.fecha>=fecha_manana, Sesion.fecha<=fecha_sabado, Sesion.cupos_disponibles>0).all()
            sesiones_speakout_hoy = Sesion.query.filter(Sesion.activo==1, Sesion.seccion=='Speak Out', Sesion.fecha==fecha_hoy, Sesion.hora>=hora_hoy, Sesion.cupos_disponibles>0).all()

            if seccion_correspondiente == 'Working':
                working_actual = working_completado + 1
                speakout_actual = working_actual + 1
                essential_actual = working_actual + 1
            elif seccion_correspondiente == 'Essential':
                essential_actual = essential_completado + 1
                working_actual = essential_actual + 1
                speakout_actual = essential_actual + 1
            else:
                speakout_actual = speakout_completado + 1
                essential_actual = speakout_actual + 1
                working_actual = speakout_actual + 1
            
            if working_actual == essential_actual and working_actual == speakout_actual and essential_actual == speakout_actual: # mostrar todas las sesiones
                
                

                if sesiones_inscritas_working or sesiones_asistidas_working:
                    print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                else: # anadir sesiones disponibles no canceladas
                    if sesiones_working:
                        for sesion in sesiones_working:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)
                                
                    if sesiones_working_hoy:
                        for sesion in sesiones_working_hoy:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)

                if sesiones_inscritas_essential or sesiones_asistidas_essential:
                    print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                else: # anadir sesiones disponibles no canceladas
                    if sesiones_essential:
                        for sesion in sesiones_essential:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)
                    if sesiones_essential_hoy:
                        for sesion in sesiones_essential_hoy:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)

                if sesiones_inscritas_speakout or sesiones_asistidas_speakout:
                    print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                else: # anadir sesiones disponibles no canceladas
                    if sesiones_speakout:
                        for sesion in sesiones_speakout:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)
                    if sesiones_speakout_hoy:
                        for sesion in sesiones_speakout_hoy:
                            flag = True
                            if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                    flag = False
                            if sesion.id_sesion not in ids_cancelados and flag:
                                respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                sesiones_disponibles.append(respuesta)
            else: # mostrar solo las menores
                menor = 52
                if working_actual<menor:
                    menor = working_actual
                if essential_actual<menor:
                    menor = essential_actual
                if speakout_actual<menor:
                    menor = speakout_actual

                if menor == working_actual: #MOSTRAR SESINOES WORKING
                    if sesiones_inscritas_working or sesiones_asistidas_working:
                        print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                    else: # anadir sesiones disponibles no canceladas
                        if sesiones_working:
                            for sesion in sesiones_working:
                                nivel_inicial = int(str(sesion.nivel).split('-')[0])
                                nivel_final = int(str(sesion.nivel).split('-')[1])
                                if nivel_inicial <= working_actual and working_actual <= nivel_final:
                                    flag = True
                                    if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                        if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                            flag = False
                                    if sesion.id_sesion not in ids_cancelados and flag:
                                        respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                        sesiones_disponibles.append(respuesta)
                        if sesiones_working_hoy:
                            for sesion in sesiones_working_hoy:
                                nivel_inicial = int(str(sesion.nivel).split('-')[0])
                                nivel_final = int(str(sesion.nivel).split('-')[1])
                                if nivel_inicial <= working_actual and working_actual <= nivel_final:
                                    flag = True
                                    if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                        if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                            flag = False
                                    if sesion.id_sesion not in ids_cancelados and flag:
                                        respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                        sesiones_disponibles.append(respuesta)
                if menor == essential_actual: #MOSTRAR SESIONES ESSENTIAL
                    if sesiones_inscritas_essential or sesiones_asistidas_essential:
                        print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                    else: # anadir sesiones disponibles no canceladas
                        if sesiones_essential:
                            for sesion in sesiones_essential:
                                nivel_inicial = int(str(sesion.nivel).split('-')[0])
                                nivel_final = int(str(sesion.nivel).split('-')[1])
                                if nivel_inicial <= essential_actual and essential_actual <= nivel_final:
                                    flag = True
                                    if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                        if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                            flag = False
                                    if sesion.id_sesion not in ids_cancelados and flag:
                                        respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                        sesiones_disponibles.append(respuesta)
                        if sesiones_essential_hoy:
                            for sesion in sesiones_essential_hoy:
                                nivel_inicial = int(str(sesion.nivel).split('-')[0])
                                nivel_final = int(str(sesion.nivel).split('-')[1])
                                if nivel_inicial <= essential_actual and essential_actual <= nivel_final:
                                    flag = True
                                    if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                        if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                            flag = False
                                    if sesion.id_sesion not in ids_cancelados and flag:
                                        respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                        sesiones_disponibles.append(respuesta)
                if menor == speakout_actual: #MOSTRAR SESINOES SPEAK
                    if sesiones_inscritas_speakout or sesiones_asistidas_speakout:
                        print("existen sesiones inscritas o que asistio pero no fue calificado del working")
                    else: # anadir sesiones disponibles no canceladas
                        if sesiones_speakout:
                            for sesion in sesiones_speakout:
                                nivel_inicial = int(str(sesion.nivel).split('-')[0])
                                nivel_final = int(str(sesion.nivel).split('-')[1])
                                if nivel_inicial <= speakout_actual and speakout_actual <= nivel_final:
                                    flag = True
                                    if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                        if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                            flag = False
                                    if sesion.id_sesion not in ids_cancelados and flag:
                                        respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                        sesiones_disponibles.append(respuesta)
                        if sesiones_speakout_hoy:
                            for sesion in sesiones_speakout_hoy:
                                nivel_inicial = int(str(sesion.nivel).split('-')[0])
                                nivel_final = int(str(sesion.nivel).split('-')[1])
                                if nivel_inicial <= speakout_actual and speakout_actual <= nivel_final:
                                    flag = True
                                    if sesion.fecha.strftime("%Y-%m-%d") in dias_fechas:
                                        if sesion.hora.strftime("%H:%M:%S") in dias_fechas[sesion.fecha.strftime("%Y-%m-%d")]:
                                            flag = False
                                    if sesion.id_sesion not in ids_cancelados and flag:
                                        respuesta = SerializadorUniversal.serializar_unico(dato=sesion, campos_requeridos=datos_requeridos)
                                        sesiones_disponibles.append(respuesta)

        #aqui se deberia retornar los valores de las sesiones disponibles

        sesiones_calendario = {}

        print(sesiones_disponibles)

        for sesion in sesiones_disponibles:
            if sesion['hora'].strftime("%H:%M") not in sesiones_calendario:
                sesiones_calendario[sesion['hora'].strftime("%H:%M")] = {}
            if sesion['fecha'].strftime("%Y-%m-%d") not in sesiones_calendario[sesion['hora'].strftime("%H:%M")]:
                sesiones_calendario[sesion['hora'].strftime("%H:%M")][sesion['fecha'].strftime("%Y-%m-%d")] = []
            
            sesiones_calendario[sesion['hora'].strftime("%H:%M")][sesion['fecha'].strftime("%Y-%m-%d")].append(sesion)
        
        

        return sesiones_disponibles, sesiones_calendario, hora_hoy, dia_actual, f_lunes, f_sabado
        
        


    def obtener_sesiones_pasadas_estudiante_id(id_estudiante):
        estudiante = Estudiante.query.filter(Estudiante.activo==1, Estudiante.id_estudiante==id_estudiante).first()
        if not estudiante:
            return None
        
        fecha_actual = datetime.now()
        fecha_string = fecha_actual.strftime("%Y-%m-%d")
        sesiones_detalles = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, DetalleSesion.id_sesion==Sesion.id_sesion).filter(DetalleSesion.id_estudiante==id_estudiante, Sesion.fecha<=fecha_string).order_by(Sesion.fecha, Sesion.hora).all()

        if not sesiones_detalles:
            return None
        
        sesiones_pasadas = []


        datos_requeridos = ['id_sesion', 'fecha', 'hora', 'seccion', 'nivel', 'activo', 'tipo_virtual']
        for sesion, detalle in sesiones_detalles:
            dict_sesion = SerializadorUniversal.serializar_unico(sesion, datos_requeridos)
            nivel = int(detalle.nivel_seccion)
            if (sesion.seccion == 'Test Oral' or sesion.seccion=='Test Escrito'):
                nivel = str(nivel-4) + "-" + str(nivel)
            elif(sesion.seccion=='Welcome'):
                nivel = '0'
            else:
                nivel = str(nivel+1)
            
            dict_sesion['nivel'] = nivel
            sesiones_pasadas.append(dict_sesion)
        
        return sesiones_pasadas


