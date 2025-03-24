from app.services.serviciosAdministrador import serviciosAdministrador

from datetime import date, time

def iniciar_datos():

    administrador = serviciosAdministrador.obtener_todos()

    if not administrador:
        nuevo_administrador = serviciosAdministrador.crear('administrador', 'administrador', 'administrador@gmail.com', 'administrador', 'administrador', '10000000', 77777777, 77777777, 'LP')
        print("usuario admin creado")