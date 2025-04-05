from app.models.docente import Docente
from app.models.horario import Horario
from app.models.sesion import Sesion
from app.models.detalleSesion import DetalleSesion
from app.models.estudiante import Estudiante
from app.models.tarea import Tarea
from app.models.detalleTarea import DetalleTarea

from app.config.extensiones import db
from app import SQLAlchemyError
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.services.serviciosSesion import ServiciosSesion
from datetime import datetime, timedelta

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from datetime import datetime
import queue
from io import BytesIO

class ServiciosReportes():
    def generar_reporte_de_sesion_pdf(nombre_usuario, id_sesion):

        sesion = Sesion.query.filter(Sesion.activo==1, Sesion.id_sesion == id_sesion).first()
        
        if not sesion:
            return None
        detalles = db.session.query(Estudiante, DetalleSesion).join(DetalleSesion, DetalleSesion.id_estudiante==Estudiante.id_estudiante).filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
        #detalles = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
        docente = Docente.query.get(sesion.id_docente)
        

        

        


        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        elementos = []

        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('Titulo', fontSize=18, alignment=1, fontName="Helvetica-Bold", underline=True)
        estilo_subtitulo_2 = ParagraphStyle('Subtitulo', fontSize=15, alignment=0)  
        estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=10, alignment=0) 
        estilo_datos = estilos['Normal']
        estilo_centrado_grande = ParagraphStyle('Centrado', fontSize=30, alignment=0)

        cabecera = [Paragraph("Hora", estilo_subtitulo), Paragraph(f"{sesion.seccion} {sesion.nivel}", estilo_subtitulo), '', Paragraph(f"{sesion.fecha.strftime('%d/%m/%Y')}", estilo_subtitulo), Paragraph(f"T. {docente.nombres} {docente.apellidos}", estilo_subtitulo)]
        segunda_cabecera = [f"{sesion.hora.strftime('%H:%M')}", Paragraph(f"N°", estilo_subtitulo), Paragraph(f"Estudiante", estilo_subtitulo), Paragraph(f"Show / No Show", estilo_subtitulo), Paragraph(f"Total Students", estilo_subtitulo)]
        tabla_registros = []
        tabla_registros.append(cabecera)
        tabla_registros.append(segunda_cabecera)
        for i in range(0,10, 1):
            fila = ['', str(i+1), '', '', '']
            tabla_registros.append(fila)
        
        ind = 2
        if detalles:
            for estudiante, detalle in detalles:
                tabla_registros[ind][2] = Paragraph(f"{estudiante.nombres} {estudiante.apellidos}", estilo_subtitulo)
                tabla_registros[ind][3] = Paragraph(f"{detalle.nivel_seccion}", estilo_subtitulo)
                ind = ind + 1
        
        imagen_clase = ''
        if sesion.imagen_url:
            ruta_imagen = os.path.join(os.getcwd(), 'app', 'static', str(sesion.imagen_url))
            imagen_clase = Image(ruta_imagen)
            imagen_width = imagen_clase.drawWidth
            imagen_height = imagen_clase.drawHeight

            # Definir el tamaño máximo de la celda
            celda_width = 1.8 * inch  # Ancho máximo de la celda que contiene la imagen
            celda_height = 1.8 * inch  # Alto máximo de la celda que contiene la imagen

            # Ajustar el tamaño de la imagen para que no se deforme
            imagen_width = min(imagen_width, celda_width)
            imagen_height = min(imagen_height, celda_height)
            imagen_clase.drawWidth = imagen_width
            imagen_clase.drawHeight = imagen_height

        # Definir los anchos de las columnas
        col_widths = [ 1.5 * inch,  0.5 * inch, 2 * inch, 1 * inch, 2 * inch]  # Ancho de cada columna
                
        tabla_registros[2][4] = imagen_clase
        





        logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 1 * inch, 1 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo)
        # Agregar elementos al PDF
        elementos.append(Spacer(1, 55))
       
        elementos.append(Spacer(1, 20))

        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.5 * inch), height - (0.5 * inch) - imagen_logo.drawHeight)
            titulo_x = width / 2  
            titulo_y = height - (1.5 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x - 120, titulo_y, "Informe de Sesión")
            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        elementos.append(Spacer(1, 20))

        tabla_registros_pdf = Table(tabla_registros, colWidths=col_widths)

        estilo_tabla = TableStyle([('BACKGROUND', (0, 0), (-1, 1), colors.gray),
                                   ('BACKGROUND', (0, 0), (0, -1), colors.gray),
                                   ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                                   ('FONTSIZE', (1, 0), (-1, -1), 12),
                                   ('FONTSIZE', (0, 1), (0, -1), 30),
                                   ('SPAN', (1, 0), (2, 0)),
                                   ('SPAN', (0, 1), (0, -1)),
                                   ('SPAN', (-1, 2), (-1, -1)),
                                   ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        
        tabla_registros_pdf.setStyle(estilo_tabla)

        elementos.append(tabla_registros_pdf)
        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer