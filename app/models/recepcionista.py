from app.models.usuario import Usuario
from app.config.extensiones import db

class Recepcionista(Usuario):
    __tablename__ = 'recepcionistas'

    id_recepcionista = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), primary_key=True)
    telefono_personal = db.Column(db.Integer, nullable=True)
    activo = db.Column(db.Integer, nullable=False, default=1)

    __mapper_args__ = {
        'polymorphic_identity': 'recepcionista'
    }

    def __init__(self, nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, telefono_personal, extension):
        super().__init__(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, rol='recepcionista', extension=extension)
        self.telefono_personal = telefono_personal
    
    def modificar_usuario(self, usuario, nuevos_datos: dict):
        for clave, valor in nuevos_datos.items():
            if hasattr(usuario, clave):
                setattr(usuario, clave, valor)
        
        try:
            db.session.commit()
            return usuario
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al modificar usuario: {str(e)}")
    
    def crear_usuario(self, datos: dict):
        rol = datos.get('rol')
        if rol=='recepcionista':
            nuevo_usuario = Recepcionista(datos.get('nombre_usuario'), datos.get('contrasena'), datos.get('correo'), datos.get('nombres'), datos.get('apellidos'), datos.get('carnet'), datos.get('telefono'), datos.get('telefono_personal'))
        
            