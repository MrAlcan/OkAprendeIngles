from app.config.extensiones import db

class Horario(db.Model):
    __tablename__ = 'horarios'

    id_horario = db.Column(db.Integer, primary_key=True)
    id_docente = db.Column(db.Integer, db.ForeignKey('docentes.id_docente'), nullable=False)
    dia = db.Column(db.String(10), nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_final = db.Column(db.Time, nullable=False)
    activo = db.Column(db.Integer, nullable=False, default=1)

    def __init__(self, docente, dia, inicio, final):
        self.id_docente = docente
        self.dia = dia
        self.hora_inicio = inicio
        self.hora_final = final
    