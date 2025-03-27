from app.config.extensiones import db
from datetime import datetime

class Sesion(db.Model):
    __tablename__ = 'sesiones'

    id_sesion = db.Column(db.Integer, nullable=False, primary_key=True)
    fecha = db.Column(db.Date, nullable=True)
    hora = db.Column(db.Time, nullable=True)
    id_docente = db.Column(db.Integer, db.ForeignKey('docentes.id_docente'), nullable=False)
    seccion = db.Column(db.String(20), nullable=False)
    nivel = db.Column(db.String(10), nullable=False, default='1-5')
    cupos_disponibles = db.Column(db.Integer, nullable=False, default=6)
    link = db.Column(db.Text, nullable=True, default=None)
    imagen_url = db.Column(db.Text, nullable=True, default=None)
    activo = db.Column(db.Integer, nullable=False, default=1)
    #Estudiantes Registrados

    def __init__(self, fecha, hora, docente, seccion, nivel=None, cupos=None):
        self.fecha = fecha
        self.hora = hora
        self.id_docente = docente
        self.seccion = seccion
        self.nivel = nivel
        self.cupos_disponibles = cupos
    
    def verificar_cupo(self):
        return True if self.cupos_disponibles - 1 >= 0 else False
    
    def disminuir_cupos(self):
        self.cupos_disponibles = self.cupos_disponibles - 1
    
    def aumetar_cupos(self):
        self.cupos_disponibles = self.cupos_disponibles + 1
    
    
