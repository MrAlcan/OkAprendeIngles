from app.config.extensiones import db

class DetalleTarea(db.Model):
    __tablename__ = 'detalles_tareas'

    id_detalle_tarea = db.Column(db.Integer, primary_key=True)
    id_tarea = db.Column(db.Integer, db.ForeignKey('tareas.id_tarea'), nullable = False)
    id_estudiante = db.Column(db.Integer, db.ForeignKey('estudiantes.id_estudiante'), nullable=False)
    material_subido = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Integer, nullable=False, default=1)

    def __init__(self, tarea, estudiante, material):
        self.id_tarea = tarea
        self.id_estudiante = estudiante
        self.material_subido = material