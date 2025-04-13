from app.models.recepcionista import Recepcionista
from app.config.extensiones import db, bcrypt
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal

class ServiciosRecepcionista():



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

            validacion = Recepcionista.query.filter(Recepcionista.nombre_usuario==nombre_usuario).first()
            if validacion:
                nombre_usuario = nombre_usuario + "." + segundo_apellido
                validacion_2 = Recepcionista.query.filter(Recepcionista.nombre_usuario==nombre_usuario).first()
                if validacion_2:
                    numeracion = True
                    contador = 0
                    nombre_usuario = nombre_usuario + "."
                    while numeracion:
                        contador = contador + 1
                        nombre_usuario_n = nombre_usuario + str(contador)
                        validacion_3 = Recepcionista.query.filter(Recepcionista.nombre_usuario==nombre_usuario_n).first()
                        if not validacion_3:
                            numeracion = False
                            nombre_usuario = nombre_usuario_n
                            break
            nuevo_recepcionista = Recepcionista(nombre_usuario, str(carnet), correo, nombres, apellidos, carnet, telefono, telefono_personal, extension)

            db.session.add(nuevo_recepcionista)
            db.session.commit()
            return {"status": "success", "message": "Recepcionista creado exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
        
    def obtener_todos():
        datos = Recepcionista.query.filter_by(activo = 1)
        datos_requeridos = ['id_recepcionista', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'telefono_personal', 'extension']
        respuesta = SerializadorUniversal.serializar_lista(datos= datos, campos_requeridos= datos_requeridos)
        return respuesta
        
    def actualizar(id_recepcionista, nombre_usuario, correo, nombres, apellidos, carnet, telefono):
        try:

            recepcionista = Recepcionista.query.get(id_recepcionista)
            recepcionista.nombre_usuario = nombre_usuario
            recepcionista.correo = correo
            recepcionista.nombres = nombres
            recepcionista.apellidos = apellidos
            recepcionista.carnet_identidad = carnet
            recepcionista.telefono = telefono
            recepcionista.contrasena_hash = bcrypt.generate_password_hash(str(carnet)).decode('utf-8')
            
            db.session.commit()

            return {"status": "success", "message": "Recepcionistas modificadas exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
    
    def eliminar(id_recepcionista):
        recepcionista = Recepcionista.query.get(id_recepcionista)

        if recepcionista:
            recepcionista.activo = 0
            db.session.commit()
        return {"status": "success", "message": "Recepcionista eliminado exitosamente"}
