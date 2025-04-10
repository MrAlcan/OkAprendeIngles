from app.config.extensiones import db
from app.models.usuario import Usuario
from datetime import datetime

class Estudiante(Usuario):
    __tablename__ = 'estudiantes'

    id_estudiante = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), primary_key=True)
    celular_titular = db.Column(db.Integer, nullable=True)
    nombres_titular = db.Column(db.String(100), nullable=False)
    nombre_nivel = db.Column(db.String(20), nullable=False, default='Basico')
    rango_nivel = db.Column(db.String(10), nullable=False, default='1-5')
    speakout_completado = db.Column(db.Integer, nullable=True, default=0)
    working_completado = db.Column(db.Integer, nullable=True, default=0)
    essential_completado = db.Column(db.Integer, nullable=True, default=0)
    welcome_completado = db.Column(db.Integer, nullable=True, default = 0)
    activo = db.Column(db.Integer, nullable=False, default=1)
    ocupacion_tutor = db.Column(db.String(30), nullable=True)
    parentesco_tutor = db.Column(db.String(7), nullable=False)
    numero_cuenta = db.Column(db.Integer, nullable=False)
    numero_contrato = db.Column(db.Integer, nullable=False)
    inicio_contrato = db.Column(db.Date, nullable=False)
    fin_contrato = db.Column(db.Date, nullable=False)
    paso_examen = db.Column(db.Integer, default=0)
    # ver de la lista de ids

    __mapper_args__ = {
        'polymorphic_identity': 'estudiante'
    }

    def __init__(self, nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, telefono_titular, nombres_titular, nombre_nivel = None, rango_nivel = None, extension=None, ocupacion_tutor=None, parentesco_tutor=None, numero_cuenta=None, numero_contrato=None, inicio_contrato=None, fin_contrato=None):
        super().__init__(nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, rol='estudiante', extension=extension)
        self.celular_titular = telefono_titular
        self.nombres_titular = nombres_titular
        self.rango_nivel = rango_nivel
        self.nombre_nivel = nombre_nivel
        self.ocupacion_tutor = ocupacion_tutor
        self.parentesco_tutor = parentesco_tutor
        self.numero_cuenta = numero_cuenta
        self.numero_contrato = numero_contrato
        if not inicio_contrato:
            inicio_contrato = datetime.now()
            inicio_contrato = inicio_contrato.strftime("%Y-%m-%d")
        if not fin_contrato:
            fin_contrato = datetime.now()
            fin_contrato = fin_contrato.strftime("%Y-%m-%d")
        self.inicio_contrato = inicio_contrato
        self.fin_contrato = fin_contrato
    
    def reservar_sesion(self, id_sesion):
        ''