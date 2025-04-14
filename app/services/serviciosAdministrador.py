from app.models.administrador import Administrador
from app.models.estudiante import Estudiante
from app.models.sesion import Sesion
from app.models.detalleSesion import DetalleSesion

from app.config.extensiones import db, bcrypt
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal

from datetime import date, datetime, timedelta

class serviciosAdministrador():


    def crear(correo, nombres, apellidos, carnet, telefono, telefono_personal, extension):
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

            validacion = Administrador.query.filter(Administrador.nombre_usuario==nombre_usuario).first()
            if validacion:
                nombre_usuario = nombre_usuario + "." + segundo_apellido
                validacion_2 = Administrador.query.filter(Administrador.nombre_usuario==nombre_usuario).first()
                if validacion_2:
                    numeracion = True
                    contador = 0
                    nombre_usuario = nombre_usuario + "."
                    while numeracion:
                        contador = contador + 1
                        nombre_usuario_n = nombre_usuario + str(contador)
                        validacion_3 = Administrador.query.filter(Administrador.nombre_usuario==nombre_usuario_n).first()
                        if not validacion_3:
                            numeracion = False
                            nombre_usuario = nombre_usuario_n
                            break

            nuevo_administrador = Administrador(nombre_usuario, str(carnet), correo, nombres, apellidos, carnet, telefono, telefono_personal, extension)

            db.session.add(nuevo_administrador)
            db.session.commit()
            return {"status": "success", "message": "Administrador creado exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
        
    def obtener_todos():
        datos = Administrador.query.filter_by(activo = 1)
        datos_requeridos = ['id_administrador', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'telefono_personal', 'extension']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        return respuesta
    
    def modificar_contrasena(id, contrasena_antigua, contrasena_nueva):
        administrador = Administrador.query.get(id)
        if administrador:
            contrasena_hash = administrador.contrasena_hash
            resultado = bcrypt.check_password_hash(contrasena_hash, contrasena_antigua)
            if resultado:
                nueva_contrasena_hash = bcrypt.generate_password_hash(contrasena_antigua).decode('utf-8')
                administrador.contrasena_hash = nueva_contrasena_hash
                db.session.commit()
            else:
                return "contrasena no coincide"
        else:
            return "no se encontro el administrador"


    def actualizar(id_administrador, nombre_usuario, correo, nombres, apellidos, carnet, telefono):
        try:

            administrador = Administrador.query.get(id_administrador)
            administrador.nombre_usuario = nombre_usuario
            administrador.correo = correo
            administrador.nombres = nombres
            administrador.apellidos = apellidos
            administrador.carnet_identidad = carnet
            administrador.telefono = telefono
            administrador.contrasena_hash = bcrypt.generate_password_hash(str(carnet)).decode('utf-8')
            
            db.session.commit()

            return {"status": "success", "message": "Administradores modificados exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
    
    def eliminar(id_administrador):
        administrador = Administrador.query.get(id_administrador)

        if administrador:
            administrador.activo = 0
            db.session.commit()
        return {"status": "success", "message": "Administrador eliminado exitosamente"}


    
    def obtener_fechas_siguientes():
        hoy = datetime.now()

        dia_actual = hoy.strftime("%A")

        dias_espanol = {
            "Monday": "Lunes",
            "Tuesday": "Martes",
            "Wednesday": "Miércoles",
            "Thursday": "Jueves",
            "Friday": "Viernes",
            "Saturday": "Sabado",
            "Sunday": "Domingo"
        }

        dia_string = dias_espanol.get(dia_actual, dia_actual)

        fechas_posibles = []

        
        for i in range(1,7):
            dia_s = hoy + timedelta(days=i)
            dia_s_h = dia_s.strftime("%A")
            dia_string = str(dias_espanol.get(dia_s_h, dia_s_h)) + " " + dia_s.strftime("%Y-%m-%d")

            cuerpo = {
                'clave': dia_s.strftime("%Y-%m-%d"),
                'valor': dia_string
            }

            if str(dias_espanol.get(dia_s_h, dia_s_h)) != 'Domingo':
                fechas_posibles.append(cuerpo)
            
        return fechas_posibles

    def obtener_estudiantes_para_sesion(id_sesion):
        sesion = Sesion.query.filter(Sesion.activo==1, Sesion.id_sesion==id_sesion).first()

        if sesion:
            if int(sesion.cupos_disponibles)>0:
                seccion_sesion = str(sesion.seccion)

                rango = sesion.nivel
                nivel_superior = 0
                nivel_inferior = 0
                if rango!='0':
                    nivel_superior = int(str(rango).split('-')[1])
                    nivel_inferior = int(str(rango).split('-')[0]) - 1
                
                estudiantes_inscritos = []
                detalle_sesion = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
                if detalle_sesion:
                    for detalle in detalle_sesion:
                        id_est = detalle.id_estudiante
                        estudiantes_inscritos.append(id_est)
                
                estudiantes = None
                if seccion_sesion == 'Welcome':
                    estudiantes = Estudiante.query.filter(Estudiante.activo==1, Estudiante.welcome_completado==0).all()
                elif seccion_sesion == 'Working':
                    estudiantes = Estudiante.query.filter(Estudiante.activo==1, Estudiante.working_completado<nivel_superior, Estudiante.working_completado>=nivel_inferior).all()
                elif seccion_sesion == 'Essential':
                    estudiantes = Estudiante.query.filter(Estudiante.activo==1, Estudiante.essential_completado<nivel_superior, Estudiante.essential_completado>=nivel_inferior).all()
                elif seccion_sesion == 'Speak Out':
                    estudiantes = Estudiante.query.filter(Estudiante.activo==1, Estudiante.speakout_completado<nivel_superior, Estudiante.speakout_completado>=nivel_inferior).all()
                else:
                    estudiantes = Estudiante.query.filter(Estudiante.activo==1, Estudiante.paso_examen==0, Estudiante.welcome_completado!=0).all()
                

                estudiantes_disponibles = []

                datos_requeridos = ['id_estudiante', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'celular_titular', 'nombres_titular', 'nombre_nivel', 'rango_nivel', 'speakout_completado', 'working_completado', 'essential_completado', 'welcome_completado', 'activo']

                if estudiantes:
                    for estud in estudiantes:
                        id_est = estud.id_estudiante
                        nivel_working = int(estud.working_completado)
                        nivel_essential = int(estud.essential_completado)
                        nivel_speakout = int(estud.speakout_completado)
                        nivel_welcome = int(estud.welcome_completado)
                        paso_examen = int(estud.paso_examen)

                        seccion_dada = 'Welcome'

                        if(nivel_welcome == 0):
                            seccion_dada = 'Welcome'
                        elif(nivel_essential == nivel_working and nivel_working == nivel_speakout and nivel_speakout%5==0 and paso_examen==0):
                            detalles = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, DetalleSesion.id_sesion==Sesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.seccion=='Test Escrito', DetalleSesion.nivel_seccion==nivel_speakout, DetalleSesion.calificacion>=85).all()
                            if detalles:
                                seccion_dada = 'Test Oral'
                            else:
                                seccion_dada = 'Test Escrito'

                        elif(nivel_essential == nivel_working and nivel_working == nivel_speakout):
                            seccion_dada = 'Essential'
                        elif(nivel_working == nivel_speakout):
                            seccion_dada = 'Working'
                        elif(nivel_essential == nivel_working):
                            seccion_dada = 'Speak Out'
                        
                        if (id_est not in estudiantes_inscritos and seccion_sesion==seccion_dada):
                            
                            respuesta = SerializadorUniversal.serializar_unico(dato= estud, campos_requeridos= datos_requeridos)
                            estudiantes_disponibles.append(respuesta)
                    return estudiantes_disponibles
                else:
                    return None

            else:
                return None

        else:
            return None



    def agregar_estudiante_manualmente(id_sesion, id_estudiante):
        sesion = Sesion.query.get(id_sesion)

        cupos = int(sesion.cupos_disponibles) - 1
        sesion.cupos_disponibles = cupos

        seccion = sesion.seccion

        nuevo_detalle = DetalleSesion(id_sesion, id_estudiante, seccion)

        db.session.add(nuevo_detalle)
        db.session.commit()
        return True

    def obtener_por_id(id_administrador):
        administrador = Administrador.query.get(id_administrador)
        if administrador:
            datos_requeridos = ['id_administrador', 'nombres', 'apellidos', 'nombre_usuario', 'carnet_identidad', 'telefono', 'correo']
            respuesta = SerializadorUniversal.serializar_unico(dato=administrador, campos_requeridos=datos_requeridos)
            return respuesta
        return None
