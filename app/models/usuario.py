from app.config.extensiones import db, bcrypt
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), nullable=False, unique=True)
    contrasena_hash = db.Column(db.Text, nullable=False)
    correo = db.Column(db.String(50), nullable=False)
    nombres = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(50), nullable=False)
    carnet_identidad = db.Column(db.String(20), nullable=False, unique=True)
    telefono = db.Column(db.Integer, nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    activo = db.Column(db.Integer, nullable=False, default=1)

    __mapper_args__ = {
        'polymorphic_identity': 'usuario',
        'polymorphic_on': rol
    }

    def __repr__(self):
        return f"Id Usuario: {self.id_usuario}, nombre_usuario: {self.nombre_usuario}, rol de usuario: {self.rol}"
    
    def __init__(self, nombre_usuario, contrasena, correo, nombres, apellidos, carnet, telefono, rol):
        self.nombre_usuario = nombre_usuario
        self.contrasena_hash = bcrypt.generate_password_hash(contrasena).decode('utf-8')
        self.correo = correo
        self.nombres = nombres
        self.apellidos = apellidos
        self.carnet_identidad = carnet
        self.telefono = telefono
        self.rol = rol
    
    def validar_contrasena(self, contrasena):
        return bcrypt.check_password_hash(self.contrasena_hash, contrasena)
    
    def actualizar_contrasena(self, antigua_contrasena, nueva_contrasena):
        if(self.validar_contrasena(antigua_contrasena)):
            self.contrasena_hash = bcrypt.generate_password_hash(nueva_contrasena).decode('utf-8')
            return True
        else:
            return False
    
    def autenticar_credenciales(self, nombre_usuario, contrasena):
        if(str(self.nombre_usuario)==str(nombre_usuario)):
            if(self.validar_contrasena(contrasena)):
                return True
            else:
                return False
        else:
            return False
    
    def modificar_datos(self, nombres, apellidos, correo, carnet, telefono):
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.carnet_identidad = carnet
        self.telefono = telefono
    
    def cerrar_sesion(self):
        'cerrar_sesion'