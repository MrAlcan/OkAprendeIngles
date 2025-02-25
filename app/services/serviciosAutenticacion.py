from app.models.usuario import Usuario
from app.config.extensiones import db
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal

class ServiciosAutenticacion():

    def autenticar_correo():
        ""