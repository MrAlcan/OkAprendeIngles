from app.config.extensiones import db

class Tarea(db.Model):
    __tablename__ = 'tareas'

    id_tarea = db.Column(db.Integer, nullable=False, primary_key=True)
    id_sesion = db.Column(db.Integer, db.ForeignKey('sesiones.id_sesion'), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    material_adicional = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Integer, nullable=False, default=1)

    def __init__(self, sesion, descripcion, material = None):
        self.id_sesion = sesion
        self.descripcion = descripcion
        self.material_adicional = material

        