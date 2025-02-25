from app.config.extensiones import db
from app.models.usuario import Usuario

class Docente(Usuario):
    __tablename__ = 'docentes'

    id_docente = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), primary_key=True)
    asignacion_tutor = db.Column(db.String(10), nullable=True, unique=False, default='TUTOR 1')

    __mapper_args__ = {
        'polymorphic_identity': 'docente'
    }

    def __init__(self, nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono):
        super().__init__(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, rol='docente')
