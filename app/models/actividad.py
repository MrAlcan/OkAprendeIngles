from app.config.extensiones import db

class Actividad(db.Model):
    __tablename__ = 'actividades'

    id_actividad = db.Column(db.Integer, nullable=False, primary_key=True)
    fecha = db.Column(db.Date, nullable=True)
    hora = db.Column(db.Time, nullable=True)
    id_docente = db.Column(db.Integer, db.ForeignKey('docentes.id_docente'), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    nivel = db.Column(db.String(10), nullable=False, default='1-5')
    cupos_disponibles = db.Column(db.Integer, nullable=True, default=0)

    def __init__(self, fecha, hora, docente, descripcion, nivel, cupos):
        self.fecha = fecha
        self.hora = hora
        self.id_docente = docente
        self.descripcion = descripcion
        self.nivel = nivel
        self.cupos_disponibles = cupos