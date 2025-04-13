from app.services.serviciosAdministrador import serviciosAdministrador
from app.models.docente import Docente
from app.models.estudiante import Estudiante
from app.models.sesion import Sesion
from app.models.detalleSesion import DetalleSesion

from app.config.extensiones import db
import os

import pandas as pd
from dateutil.relativedelta import relativedelta

from datetime import date, time, datetime, timedelta

diccionario_docentes = {}
diccionario_estudiantes = {}
diccionario_sesiones = {}


direccion_actual = os.path.join(os.getcwd(), 'app', 'config')

def iniciar_datos():

    flag_estudiantes = False

    administrador = serviciosAdministrador.obtener_todos()
    docentes = Docente.query.all()
    estudiantes = Estudiante.query.all()
    sesiones = Sesion.query.all()
    detalles = DetalleSesion.query.all()

    if not administrador:

        nuevo_administrador = serviciosAdministrador.crear('administrador@gmail.com', 'administrador', 'administrador', '10000000', 77777777, 77777777, 'LP')

        print("usuario admin creado")
    
    if not docentes:
        print("creando docentes")
        
        archivo_csv1 = 'tutores_unicos.csv'
        archivo_csv1 = os.path.join(direccion_actual, archivo_csv1)
        df1 = pd.read_csv(archivo_csv1, sep=";")
        for index, row in df1.iterrows():
            
            tutor = str(row['tutor'])
            nombres = str(row['nombres']).title()
            apellidos = str(row['apellidos']).title()
            correo = str(row['correo'])
            carnet = str(row['carnet'])
            telefono = str(row['telefono'])
            color = str(row['color'])
            asignacion_tutor = str(row['asignacion_tutor'])
            extension = str(row['extension'])


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

            diccionario_docentes[tutor] = id_docente
            
        #

        '''docentes_objs = Docente.query.all()

        for docente_objs in docentes_objs:
            id_docente = docente_objs.id_docente

            diccionario_docentes[tutor] = id_docente'''

        print(diccionario_docentes)
    

    if not estudiantes:
        print("creando estudiantes")
        flag_estudiantes = True
        
        archivo_csv1 = 'registro_estudiantes_completos_fin_06-04-2025.csv'
        archivo_csv1 = os.path.join(direccion_actual, archivo_csv1)
        df1 = pd.read_csv(archivo_csv1, sep=";")
        for index, row in df1.iterrows():

            correo = str(row['correo'])
            nombres = str(row['nombres']).title()
            apellidos = str(row['apellidos']).title()
            carnet = str(row['carnet'])
            telefono = str(row['telefono'])
            telefono_titular = str(row['telefono_titular'])
            nombres_titular = str(row['nombres_titular']).title()
            nombre_nivel = str(row['nombre_nivel']).title()
            rango_nivel = str(row['rango_nivel'])
            extension = str(row['extension'])
            ocupacion_tutor = str(row['ocupacion_tutor']).title()
            parentesco_tutor = str(row['parentesco_tutor']).title()
            numero_cuenta = str(row['numero_cuenta'])
            numero_contrato = str(row['numero_contrato'])
            inicio_contrato = str(row['inicio_contrato'])
            fin_contrato = str(row['fin_contrato'])
            welcome_c = str(row['welcome_c'])
            essential_c = str(row['essential_c'])
            working_c = str(row['working_c'])
            speak_c = str(row['speak_c'])
            
            


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



            nuevo_estudiante = Estudiante(nombre_usuario, str(carnet), correo, nombres, apellidos, carnet, telefono, telefono_titular, nombres_titular, nombre_nivel, rango_nivel, extension, ocupacion_tutor, parentesco_tutor, numero_cuenta, numero_contrato, inicio_contrato, fin_contrato)
            db.session.add(nuevo_estudiante)
            db.session.commit()

            id_estudiante = nuevo_estudiante.id_estudiante

            nuevo_estudiante.welcome_completado = welcome_c
            nuevo_estudiante.working_completado = working_c
            nuevo_estudiante.essential_completado = essential_c
            nuevo_estudiante.speakout_completado = speak_c
            db.session.commit()

            diccionario_estudiantes[carnet] = id_estudiante
        
        print(diccionario_estudiantes)
    

    if not sesiones:
        print("creando sesiones")
        
        archivo_csv1 = 'sesiones_unicas_rango_nivel.csv'
        archivo_csv1 = os.path.join(direccion_actual, archivo_csv1)
        df1 = pd.read_csv(archivo_csv1, sep=",")
        for index, row in df1.iterrows():

            rango_nivel = str(row['rango_nivel'])

            id_sesion = str(row['id_sesion'])
            fecha = str(row['fecha'])
            hora = str(row['hora'])
            seccion = str(row['seccion']).title()
            tutor = str(row['tutor'])
            if seccion.startswith('Working'):
                seccion = 'Working'
            elif seccion.startswith('Test'):
                seccion = 'Test'

            id_docente = diccionario_docentes[tutor]

            nueva_sesion = Sesion(fecha, hora, id_docente, seccion, rango_nivel, 6, 1)
            db.session.add(nueva_sesion)
            db.session.commit()

            id_sesion_obj = nueva_sesion.id_sesion
            diccionario_sesiones[id_sesion] = id_sesion_obj
        #db.session.commit()
    
    if not detalles:
        print("creando detalles")
        
        archivo_csv1 = 'detalle_sesiones_final_con_estados.csv'
        archivo_csv1 = os.path.join(direccion_actual, archivo_csv1)
        df1 = pd.read_csv(archivo_csv1, sep=",")

        for index, row in df1.iterrows():

            carnet = str(row['carnet'])
            nota = str(row['nota'])
            numero_sesion = str(row['numero_sesion'])
            id_sesion = str(row['id_sesion'])
            estado_registro = str(row['estado_registro'])

            id_estudiante = diccionario_estudiantes[carnet]
            id_sesion_obj = diccionario_sesiones[id_sesion]

            nuevo_detalle = DetalleSesion(id_sesion_obj, id_estudiante, numero_sesion)

            db.session.add(nuevo_detalle)
            db.session.commit()
            nuevo_detalle.calificacion = float(nota)
            nuevo_detalle.estado_registro = estado_registro
            db.session.commit()
        #db.session.commit()

    if flag_estudiantes:
        estudiantes = Estudiante.query.all()
        for estudiante in estudiantes:
            id_estudiante = estudiante.id_estudiante
            sesion_ini, detalles_ini = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, DetalleSesion.id_sesion == Sesion.id_sesion).filter(DetalleSesion.id_estudiante == id_estudiante).order_by(Sesion.fecha, Sesion.hora).first()
            detalles_fin = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, DetalleSesion.id_sesion == Sesion.id_sesion).filter(DetalleSesion.id_estudiante == id_estudiante).order_by(Sesion.fecha.desc(), Sesion.hora.desc()).all()
            fecha_primera_sesion = sesion_ini.fecha
            welcome_c = 0
            working_c = 0
            essential_c = 0
            speakout_c = 0
            paso_examen = 0
            fecha_ultima_sesion = 0
            contador = 0

            tests_aprobados = 0

            for sesion, detalle in detalles_fin:
                seccion_sesion = sesion.seccion
                nivel_sesion = detalle.nivel_seccion
                calificacion = detalle.calificacion
                if contador==0:
                    fecha_ultima_sesion = sesion.fecha
                contador = contador + 1
                if (seccion_sesion == 'Welcome' and contador==1):
                    if calificacion>=85:
                        paso_examen = 1
                        welcome_c = 1
                    break
                elif (seccion_sesion == 'Working' and contador==1):
                    welcome_c = 1
                    if calificacion>=85:
                        working_c = nivel_sesion + 1
                        essential_c = nivel_sesion + 1
                        speakout_c = nivel_sesion
                    else:
                        working_c = nivel_sesion
                        essential_c = nivel_sesion + 1
                        speakout_c = nivel_sesion
                    break
                elif (seccion_sesion == 'Essential' and contador==1):
                    welcome_c = 1
                    if calificacion>=85:
                        working_c = nivel_sesion
                        essential_c = nivel_sesion + 1
                        speakout_c = nivel_sesion
                    else:
                        working_c = nivel_sesion
                        essential_c = nivel_sesion
                        speakout_c = nivel_sesion
                    break
                elif (seccion_sesion == 'Speak Out' and contador==1):
                    welcome_c = 1
                    if calificacion>=85:
                        working_c = nivel_sesion + 1
                        essential_c = nivel_sesion + 1
                        speakout_c = nivel_sesion + 1
                    else:
                        working_c = nivel_sesion + 1
                        essential_c = nivel_sesion + 1
                        speakout_c = nivel_sesion
                    break
                welcome_c = 1
                working_c = nivel_sesion
                essential_c = nivel_sesion
                speakout_c = nivel_sesion
                #paso_examen = 1
                if (seccion_sesion=='Working' or seccion_sesion=='Essential' or seccion_sesion=='Speak Out'):
                    break

                if calificacion>=85:
                    tests_aprobados = tests_aprobados + 1
                
            

            if tests_aprobados >= 2:
                paso_examen = 1
            
            estudiante.welcome_completado = welcome_c
            estudiante.working_completado = working_c
            estudiante.essential_completado = essential_c
            estudiante.speakout_completado = speakout_c
            estudiante.paso_examen = paso_examen

            if estudiante.inicio_contrato.strftime("%Y-%m-%d") == "2025-04-10" or estudiante.fin_contrato.strftime("%Y-%m-%d") == "2025-04-10":
                estudiante.inicio_contrato = fecha_primera_sesion
                ultima_sesion_est = fecha_primera_sesion + relativedelta(years=1)

                if fecha_ultima_sesion <= ultima_sesion_est:
                    estudiante.fin_contrato = ultima_sesion_est
                else:
                    ultima_sesion_est = ultima_sesion_est + relativedelta(years=1)
                    estudiante.fin_contrato = ultima_sesion_est
            

            db.session.commit()




            
    
