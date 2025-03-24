from app.models.administrador import Administrador
from app.config.extensiones import db, bcrypt
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal

class serviciosAdministrador():

    def crear(correo, nombres, apellidos, carnet, telefono, telefono_personal):
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

            nuevo_administrador = Administrador(nombre_usuario, str(carnet), correo, nombres, apellidos, carnet, telefono, telefono_personal)
            db.session.add(nuevo_administrador)
            db.session.commit()
            return {"status": "success", "message": "Administrador creado exitosamente"}
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
        
    def obtener_todos():
        datos = Administrador.query.filter_by(activo = 1)
        datos_requeridos = ['id_administrador', 'nombre_usuario', 'correo', 'nombres', 'apellidos', 'carnet_identidad', 'telefono', 'rol', 'telefono_personal']
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
