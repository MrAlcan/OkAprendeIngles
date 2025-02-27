from app.config.extensiones import db

class DetalleSesion(db.Model):
    __tablename__ = 'detalles_sesiones'

    id_inscritos_sesion = db.Column(db.Integer, primary_key=True)
    id_sesion = db.Column(db.Integer, db.ForeignKey('sesiones.id_sesion'), nullable=False)
    id_estudiante = db.Column(db.Integer, db.ForeignKey('estudiantes.id_estudiante'), nullable = False)
    estado_registro = db.Column(db.String(20), nullable=False, default = 'Inscrito')
    calificacion = db.Column(db.Double, nullable=False, default=0)
    justificacion = db.Column(db.String(150), nullable=True, default='S/N')
    activo = db.Column(db.Integer, nullable=False, default=1)

    def __init__(self, sesion, estudiante):
        self.id_sesion = sesion
        self.id_estudiante = estudiante
        
