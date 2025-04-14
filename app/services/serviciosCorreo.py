import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SENDER_EMAIL = "gestion.okaprendeingles@gmail.com"      # Cambia por tu correo
SENDER_PASSWORD = ""          # Cambia por tu contraseña o usa variables de entorno
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Lista de dominios válidos (puedes ampliarla según tus necesidades)
VALID_DOMAINS = {"gmail.com", "hotmail.com", "yahoo.com", "outlook.com"}


def is_valid_email(email: str) -> bool:
    """
    Valida que el correo tenga un formato adecuado y que el dominio sea uno de los permitidos.
    Retorna True si es válido, de lo contrario False.
    """
    # Validación básica con regex para el formato general
    regex = r"(^[\w\.-]+)@([\w\.-]+\.[\w]+$)"
    match = re.match(regex, email)
    if not match:
        return False
    dominio = match.group(2).lower()
    return dominio in VALID_DOMAINS

def send_email(subject: str, recipient: str, html_content: str, plain_text: str = "") -> bool:
    """
    Función genérica para enviar un correo electrónico con asunto, contenido HTML y opcionalmente contenido en texto.
    Retorna True si el envío fue exitoso, False de lo contrario.
    """
    if not is_valid_email(recipient):
        print(f"El correo {recipient} no es válido.")
        return False

    # Construir el mensaje
    msg = MIMEMultipart('alternative')
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient
    msg['Subject'] = subject

    # Agregar contenido en texto plano (fallback) y HTML
    if plain_text:
        part1 = MIMEText(plain_text, 'plain')
        msg.attach(part1)
    part2 = MIMEText(html_content, 'html')
    msg.attach(part2)

    try:
        # Conexión al servidor SMTP de Gmail usando TLS
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Correo enviado a {recipient} con asunto: '{subject}'")
        return True
    except Exception as e:
        print(f"Error al enviar el correo a {recipient}: {e}")
        return False
class ServiciosCorreo():

    # Configuración del correo Gmail remitente.
    

    

    def enviar_credenciales_nuevo_usuario(recipient: str, username: str, password: str) -> bool:
        """
        Envía un correo electrónico a un nuevo usuario con su nombre de usuario y contraseña.
        Se espera que se le proporcione el correo destino, el nombre de usuario y la contraseña.
        """
        subject = "Bienvenido a la Plataforma de Gestión de Ok Aprende Ingles"
        # Ejemplo de contenido HTML con formato profesional
        html_content = f"""
        <html>
        <head>
            <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #004080; padding: 10px; color: #fff; text-align: center; }}
            .content {{ margin: 20px; }}
            .footer {{ margin-top: 20px; font-size: 0.9em; color: #666; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
            <h2>Plataforma de Gestión</h2>
            </div>
            <div class="content">
            <p>Estimado/a <strong>{username}</strong>,</p>
            <p>Nos complace darte la bienvenida a nuestra plataforma de gestión. A continuación, encontrarás tus credenciales para acceder:</p>
            <ul>
                <li><strong>Usuario:</strong> {username}</li>
                <li><strong>Contraseña:</strong> {password}</li>
            </ul>
            
            <p>Estamos a tu disposición para cualquier duda o consulta.</p>
            </div>
            <div class="footer">
            <p>© 2025 Ok Aprende Ingles. Todos los derechos reservados.</p>
            </div>
        </body>
        </html>
        """
        plain_text = (f"Estimado/a {username},\n\n"
                    f"Nos complace darte la bienvenida a nuestra plataforma de gestión.\n"
                    f"Tus credenciales son:\nUsuario: {username}\nContraseña: {password}\n\n"
                    "Por favor, inicia sesión.\n\n"
                    "Saludos,\nOk Aprende Ingles")
        
        return send_email(subject, recipient, html_content, plain_text)

    def enviar_link_reunion(recipient: str, meeting_link: str) -> bool:
        """
        Envía un correo electrónico a los integrantes del grupo de trabajo con el link de la reunión virtual.
        Se espera que se le proporcione el correo destino y el link de la reunión.
        """
        subject = "Enlace a Reunión Virtual - Ok Aprende Ingles"
        html_content = f"""
        <html>
        <head>
            <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #005a9c; padding: 10px; color: #fff; text-align: center; }}
            .content {{ margin: 20px; }}
            .link {{ font-size: 1.2em; font-weight: bold; color: #005a9c; }}
            .footer {{ margin-top: 20px; font-size: 0.9em; color: #666; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
            <h2>Ok Aprende Ingles</h2>
            </div>
            <div class="content">
            <p>Estimado estudiante,</p>
            <p>Se ha programado una reunión virtual para la clase. Puedes acceder a la sesión en el siguiente enlace:</p>
            <p class="link"><a href="{meeting_link}" target="_blank">{meeting_link}</a></p>
            <p>Te recomendamos ingresar unos minutos antes para asegurar tu conexión y revisar la configuración de audio y video.</p>
            <p>Si tienes alguna consulta, no dudes en contactarnos.</p>
            </div>
            <div class="footer">
            <p>© 2025 Ok Aprende Ingles. Todos los derechos reservados.</p>
            </div>
        </body>
        </html>
        """
        plain_text = (f"Estimado estudiante,\n\n"
                    f"Se ha programado una reunión virtual. Ingresa al siguiente enlace:\n{meeting_link}\n\n"
                    "Te recomendamos ingresar unos minutos antes para verificar tu conexión.\n\n"
                    "Saludos,\nOk Aprende Ingles")
        
        return send_email(subject, recipient, html_content, plain_text)

