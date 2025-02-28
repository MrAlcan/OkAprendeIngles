from app.config.extensiones import db
from app.models.usuario import Usuario

class Docente(Usuario):
    __tablename__ = 'docentes'

    id_docente = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), primary_key=True)
    asignacion_tutor = db.Column(db.String(10), nullable=True, unique=False, default='TUTOR 1')
    activo = db.Column(db.Integer, nullable=False, default=1)

    __mapper_args__ = {
        'polymorphic_identity': 'docente'
    }

    def __repr__(self):
        return self.id_docente

    def __init__(self, nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, asignacion_tutor=None):
        super().__init__(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, rol='docente')
        self.asignacion_tutor = asignacion_tutor
