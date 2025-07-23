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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from datetime import datetime, date, timedelta
import queue
from io import BytesIO

DIAS_INGLES = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sabado",
    "Sunday": "Domingo"
}

def hex_to_color(hex_str):
    # Elimina el símbolo '#' si está presente
    hex_str = hex_str.lstrip('#')
    
    # Divide en componentes R, G, B
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0

    return colors.Color(r, g, b)

#logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
logo_direccion = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', 'img', 'logo.jpeg')
class ServiciosReportes():
    def generar_reporte_de_sesion_pdf(nombre_usuario, id_sesion):

        sesion = Sesion.query.filter(Sesion.activo==1, Sesion.id_sesion == id_sesion).first()
        
        if not sesion:
            return None
        detalles = db.session.query(Estudiante, DetalleSesion).join(DetalleSesion, DetalleSesion.id_estudiante==Estudiante.id_estudiante).filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
        #detalles = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
        docente = Docente.query.get(sesion.id_docente)
        color_docente = hex_to_color(docente.color)
        
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
        

        estudiantes_totales = 0
        estudiantes_asistio = 0
        
        ind = 2
        if detalles:
            for estudiante, detalle in detalles:
                tabla_registros[ind][2] = Paragraph(f"{estudiante.nombres} {estudiante.apellidos}", estilo_subtitulo)
                tabla_registros[ind][3] = Paragraph(f"{detalle.nivel_seccion}", estilo_subtitulo)
                ind = ind + 1
                if detalle.estado_registro == 'Asistio':
                    estudiantes_totales = estudiantes_totales + 1
                    estudiantes_asistio = estudiantes_asistio + 1
                elif detalle.estado_registro == 'Falto':
                    estudiantes_totales = estudiantes_totales + 1
        
        imagen_clase = ''
        if sesion.imagen_url:
            #ruta_imagen = os.path.join(os.getcwd(), 'app', 'static', str(sesion.imagen_url))
            ruta_imagen = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', str(sesion.imagen_url))
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
                
        tabla_registros[4][4] = imagen_clase
        tabla_registros[2][4] = Paragraph(f"<b>{estudiantes_asistio}/{estudiantes_totales}</b>", estilo_titulo)
        





        #logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
        #logo_direccion = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', 'img', 'logo.jpeg')
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
            canvas.drawString(titulo_x - 90, titulo_y, "Informe de Sesión")
            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        elementos.append(Spacer(1, 20))

        tabla_registros_pdf = Table(tabla_registros, colWidths=col_widths)

        estilo_tabla = TableStyle([('BACKGROUND', (0, 0), (-1, 1), color_docente),
                                   ('BACKGROUND', (0, 0), (0, -1), color_docente),
                                   ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                                   ('FONTSIZE', (1, 0), (-1, -1), 12),
                                   ('FONTSIZE', (0, 1), (0, -1), 30),
                                   ('SPAN', (1, 0), (2, 0)),
                                   ('SPAN', (0, 1), (0, -1)),
                                   ('SPAN', (-1, 2), (-1, 3)),
                                   ('SPAN', (-1, 4), (-1, -1)),
                                   ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
                                   ('VALIGN', (-1, 2), (-1, 3), 'MIDDLE'),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        
        tabla_registros_pdf.setStyle(estilo_tabla)

        elementos.append(tabla_registros_pdf)
        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer
    
    def generar_reporte_de_sesiones_por_dia_pdf(nombre_usuario, fecha):
        
        margin_left = 0.6 * inch
        margin_right = 0.6 * inch
        margin_top = 1.2 * inch  # Deja espacio para el carimbo
        margin_bottom = 1 * inch

        rojo_fuerte = colors.Color(1, 0.298, 0.298)      # #FF4C4C
        naranja_suave = colors.Color(1, 0.835, 0.502)    # #FFD580
        amarillo_claro = colors.Color(1, 1, 0.6)         # #FFFF99
        verde_claro = colors.Color(0.698, 0.949, 0.698)  # #B2F2B2

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter, 
                            leftMargin=margin_left,
                            rightMargin=margin_right,
                            topMargin=margin_top,
                            bottomMargin=margin_bottom)
        elementos = []

        

        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('Titulo', fontSize=16, alignment=1, fontName="Helvetica-Bold", underline=True)
        estilo_subtitulo_2 = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  
        estilo_subtitulo_3 = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  
        estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=6, alignment=0) 
        estilo_datos = estilos['Normal']
        estilo_centrado_grande = ParagraphStyle('Centrado', fontSize=30, alignment=0)

        

        #logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
        #logo_direccion = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 0.8 * inch, 0.8 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo_2)


        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.2 * inch), height - (0.2 * inch) - imagen_logo.drawHeight)
            titulo_x = width / 2  
            titulo_y = height - (0.7 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x - 150, titulo_y, f"Informe de Sesiones del {fecha}")
            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        #elementos.append(Spacer(1, 20))

        fecha_objetivo = datetime.strptime(fecha, "%Y-%m-%d")
        sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.fecha==fecha_objetivo).order_by(Sesion.fecha, Sesion.hora).all()

        if sesiones:
            contador = 0
            for sesion in sesiones:
                id_sesion = sesion.id_sesion
                contador = contador + 1
                
                
                detalles = db.session.query(Estudiante, DetalleSesion).join(DetalleSesion, DetalleSesion.id_estudiante==Estudiante.id_estudiante).filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
                #detalles = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
                docente = Docente.query.get(sesion.id_docente)
                color_docente = hex_to_color(docente.color)
                
                

                cabecera = [Paragraph("Hora", estilo_subtitulo_2), Paragraph(f"{sesion.seccion} {sesion.nivel}", estilo_subtitulo_2), '', '', Paragraph(f"<b>Teacher:</b> {docente.nombres} {docente.apellidos}", estilo_subtitulo_2), '', '']
                segunda_cabecera = [f"{sesion.hora.strftime('%H:%M')}", Paragraph(f"N°", estilo_subtitulo), Paragraph(f"Estudiantes", estilo_subtitulo_2), '', Paragraph(f"Show / No Show", estilo_subtitulo), Paragraph(f"Total Students", estilo_subtitulo), Paragraph(f"Foto", estilo_subtitulo_2)]
                tabla_registros = []
                tabla_registros.append(cabecera)
                tabla_registros.append(segunda_cabecera)
                for i in range(0,10, 1):
                    fila = ['', str(i+1), '', '', '', '', '']
                    tabla_registros.append(fila)
                

                estudiantes_totales = 0
                estudiantes_asistio = 0
                
                ind = 2
                if detalles:
                    for estudiante, detalle in detalles:
                        tabla_registros[ind][2] = Paragraph(f"{estudiante.nombres} {estudiante.apellidos}", estilo_subtitulo)
                        
                        tabla_registros[ind][4] = Paragraph(f"{detalle.nivel_seccion}", estilo_subtitulo)
                        
                        if detalle.estado_registro == 'Asistio':
                            tabla_registros[ind][3] = detalle.calificacion
                            estudiantes_totales = estudiantes_totales + 1
                            estudiantes_asistio = estudiantes_asistio + 1
                        elif detalle.estado_registro == 'Falto':
                            tabla_registros[ind][3] = "Falto"
                            estudiantes_totales = estudiantes_totales + 1
                        elif detalle.estado_registro == 'Cancelado':
                            tabla_registros[ind][3] = "Cancelo"
                        ind = ind + 1
                
                imagen_clase = ''
                if sesion.imagen_url:
                    #ruta_imagen = os.path.join(os.getcwd(), 'app', 'static', str(sesion.imagen_url))
                    ruta_imagen = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', str(sesion.imagen_url))
                    imagen_clase = Image(ruta_imagen)
                    imagen_width = imagen_clase.drawWidth
                    imagen_height = imagen_clase.drawHeight

                    # Definir el tamaño máximo de la celda
                    celda_width = 1.6 * inch  # Ancho máximo de la celda que contiene la imagen
                    celda_height = 1.6 * inch  # Alto máximo de la celda que contiene la imagen

                    # Ajustar el tamaño de la imagen para que no se deforme
                    imagen_width = min(imagen_width, celda_width)
                    imagen_height = min(imagen_height, celda_height)
                    imagen_clase.drawWidth = imagen_width
                    imagen_clase.drawHeight = imagen_height

                # Definir los anchos de las columnas
                col_widths = [ 0.7 * inch,  0.3 * inch, 2 * inch, 0.3*inch, 0.8 * inch, 0.8 * inch, 1.8*inch]  # Ancho de cada columna
                        
                tabla_registros[2][6] = imagen_clase
                tabla_registros[2][5] = Paragraph(f"<b>{estudiantes_asistio}/{estudiantes_totales}</b>", estilo_titulo)
                





                tabla_registros_pdf = Table(tabla_registros, colWidths=col_widths, rowHeights=0.2*inch)

                estilo_tabla = TableStyle([('BACKGROUND', (0, 0), (-1, 1), color_docente),
                                        ('BACKGROUND', (0, 0), (0, -1), color_docente),
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                                        ('FONTSIZE', (1, 0), (-1, -1), 6),
                                        ('FONTSIZE', (0, 1), (0, -1), 15),
                                        ('SPAN', (1, 0), (3, 0)),
                                        ('SPAN', (2, 1), (3, 1)),
                                        ('SPAN', (4, 0), (-1, 0)),
                                        ('SPAN', (0, 1), (0, -1)),
                                        ('SPAN', (-1, 2), (-1, -1)),
                                        ('SPAN', (5, 2), (5, -1)),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
                                        ('VALIGN', (5, 2), (5, -1), 'MIDDLE'),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])
                
                for i in range(2, 11, 1):
                    calificacion = tabla_registros[i][3]
                    if calificacion == '':
                        continue
                    if calificacion == 'Falto' or calificacion == 'Cancelo':
                        color = naranja_suave
                    elif float(calificacion)>=85.0:
                        color = verde_claro
                    elif float(calificacion)<85.0:
                        color = amarillo_claro
                    estilo_tabla.add("BACKGROUND", (3, i), (3, i), color)

                
                tabla_registros_pdf.setStyle(estilo_tabla)

                elementos.append(tabla_registros_pdf)
                if contador%3==0:

                    elementos.append(Spacer(1, 20))
                else:
                    elementos.append(Spacer(1, 40))
        else:
            elementos.append(Paragraph("Sin sesiones registradas para esta fecha"))
        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer

    
    def generar_reporte_de_sesiones_por_semana_pdf(nombre_usuario, fecha):

        

        margin_left = 0.6 * inch
        margin_right = 0.6 * inch
        margin_top = 1.2 * inch  # Deja espacio para el carimbo
        margin_bottom = 1 * inch

        rojo_fuerte = colors.Color(1, 0.298, 0.298)      # #FF4C4C
        naranja_suave = colors.Color(1, 0.835, 0.502)    # #FFD580
        amarillo_claro = colors.Color(1, 1, 0.6)         # #FFFF99
        verde_claro = colors.Color(0.698, 0.949, 0.698)  # #B2F2B2

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter, 
                            leftMargin=margin_left,
                            rightMargin=margin_right,
                            topMargin=margin_top,
                            bottomMargin=margin_bottom)
        elementos = []

        

        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('Titulo', fontSize=16, alignment=1, fontName="Helvetica-Bold", underline=True)
        estilo_subtitulo_2 = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  
        estilo_subtitulo_3 = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  
        estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=6, alignment=0) 
        estilo_datos = estilos['Normal']
        estilo_centrado_grande = ParagraphStyle('Centrado', fontSize=30, alignment=0)

        

        #logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
        #logo_direccion = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 0.8 * inch, 0.8 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo_2)


        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.2 * inch), height - (0.2 * inch) - imagen_logo.drawHeight)
            titulo_x = width / 2  
            titulo_y = height - (0.7 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x - 90, titulo_y, f"Informe de Sesiones")
            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        #elementos.append(Spacer(1, 20))

        fecha_objetivo = datetime.strptime(fecha, "%Y-%m-%d")

        fecha_date = fecha_objetivo.date()

        dias_al_lunes = fecha_date.weekday()

        fecha_lunes = fecha_date - timedelta(days=dias_al_lunes)
        fecha_sabado = fecha_lunes + timedelta(days=5)

        sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.fecha>=fecha_lunes, Sesion.fecha<=fecha_sabado).order_by(Sesion.fecha, Sesion.hora).all()

        dia_primero = 'Lunes'
        if sesiones:
            contador = 0
            for sesion in sesiones:
                dia_sesion_ing = sesion.fecha.strftime("%A")
                dia_primero = DIAS_INGLES[dia_sesion_ing]
                contador = contador + 1
                if contador == 1:
                    break

        if sesiones:
            contador_hojas = 0
            contador = 0
            contador_dias = 0
            buffer_dias = dia_primero
            for sesion in sesiones:
                id_sesion = sesion.id_sesion

                dia_sesion_ing = sesion.fecha.strftime("%A")
                fecha_str = sesion.fecha.strftime("%d/%m/%Y")
                

                if buffer_dias != DIAS_INGLES[dia_sesion_ing]:
                    contador_dias = 0
                    contador = 0

                if contador_dias == 0:
                    if contador_hojas >0:
                        elementos.append(PageBreak())
                    elementos.append(Paragraph(f"{DIAS_INGLES[dia_sesion_ing]}, {fecha_str}", estilo_titulo))
                    elementos.append(Spacer(1, 10))
                    buffer_dias = DIAS_INGLES[dia_sesion_ing]

                contador_dias = contador_dias + 1
                contador = contador + 1
                contador_hojas = contador_hojas + 1
                
                
                detalles = db.session.query(Estudiante, DetalleSesion).join(DetalleSesion, DetalleSesion.id_estudiante==Estudiante.id_estudiante).filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
                #detalles = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
                docente = Docente.query.get(sesion.id_docente)
                color_docente = hex_to_color(docente.color)
                
                

                cabecera = [Paragraph("Hora", estilo_subtitulo_3), Paragraph(f"{sesion.seccion} {sesion.nivel}", estilo_subtitulo_3), '', '', Paragraph(f"<b>Teacher:</b> {docente.nombres} {docente.apellidos}", estilo_subtitulo_3), '', '']
                segunda_cabecera = [f"{sesion.hora.strftime('%H:%M')}", Paragraph(f"N°", estilo_subtitulo), Paragraph(f"Estudiantes", estilo_subtitulo_3), '', Paragraph(f"Show / No Show", estilo_subtitulo), Paragraph(f"Total Students", estilo_subtitulo), Paragraph(f"Foto", estilo_subtitulo_3)]
                tabla_registros = []
                tabla_registros.append(cabecera)
                tabla_registros.append(segunda_cabecera)
                for i in range(0,10, 1):
                    fila = ['', str(i+1), '', '', '', '', '']
                    tabla_registros.append(fila)
                

                estudiantes_totales = 0
                estudiantes_asistio = 0
                
                ind = 2
                if detalles:
                    for estudiante, detalle in detalles:
                        tabla_registros[ind][2] = Paragraph(f"{estudiante.nombres} {estudiante.apellidos}", estilo_subtitulo)
                        
                        tabla_registros[ind][4] = Paragraph(f"{detalle.nivel_seccion}", estilo_subtitulo)
                        
                        if detalle.estado_registro == 'Asistio':
                            tabla_registros[ind][3] = detalle.calificacion
                            estudiantes_totales = estudiantes_totales + 1
                            estudiantes_asistio = estudiantes_asistio + 1
                        elif detalle.estado_registro == 'Falto':
                            tabla_registros[ind][3] = "Falto"
                            estudiantes_totales = estudiantes_totales + 1
                        elif detalle.estado_registro == 'Cancelado':
                            tabla_registros[ind][3] = "Cancelo"
                        ind = ind + 1
                
                imagen_clase = ''
                if sesion.imagen_url:
                    #ruta_imagen = os.path.join(os.getcwd(), 'app', 'static', str(sesion.imagen_url))
                    ruta_imagen = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', str(sesion.imagen_url))
                    imagen_clase = Image(ruta_imagen)
                    imagen_width = imagen_clase.drawWidth
                    imagen_height = imagen_clase.drawHeight

                    # Definir el tamaño máximo de la celda
                    celda_width = 1.6 * inch  # Ancho máximo de la celda que contiene la imagen
                    celda_height = 1.6 * inch  # Alto máximo de la celda que contiene la imagen

                    # Ajustar el tamaño de la imagen para que no se deforme
                    imagen_width = min(imagen_width, celda_width)
                    imagen_height = min(imagen_height, celda_height)
                    imagen_clase.drawWidth = imagen_width
                    imagen_clase.drawHeight = imagen_height

                # Definir los anchos de las columnas
                col_widths = [ 0.7 * inch,  0.3 * inch, 2 * inch, 0.3*inch, 0.8 * inch, 0.8 * inch, 1.8*inch]  # Ancho de cada columna
                        
                tabla_registros[2][6] = imagen_clase
                tabla_registros[2][5] = Paragraph(f"<b>{estudiantes_asistio}/{estudiantes_totales}</b>", estilo_titulo)
                





                tabla_registros_pdf = Table(tabla_registros, colWidths=col_widths, rowHeights=0.2*inch)

                estilo_tabla = TableStyle([('BACKGROUND', (0, 0), (-1, 1), color_docente),
                                        ('BACKGROUND', (0, 0), (0, -1), color_docente),
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                                        ('FONTSIZE', (1, 0), (-1, -1), 6),
                                        ('FONTSIZE', (0, 1), (0, -1), 15),
                                        ('SPAN', (1, 0), (3, 0)),
                                        ('SPAN', (2, 1), (3, 1)),
                                        ('SPAN', (4, 0), (-1, 0)),
                                        ('SPAN', (0, 1), (0, -1)),
                                        ('SPAN', (-1, 2), (-1, -1)),
                                        ('SPAN', (5, 2), (5, -1)),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
                                        ('VALIGN', (5, 2), (5, -1), 'MIDDLE'),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])
                
                for i in range(2, 11, 1):
                    calificacion = tabla_registros[i][3]
                    if calificacion == '':
                        continue
                    if calificacion == 'Falto' or calificacion == 'Cancelo':
                        color = naranja_suave
                    elif float(calificacion)>=85.0:
                        color = verde_claro
                    elif float(calificacion)<85.0:
                        color = amarillo_claro
                    estilo_tabla.add("BACKGROUND", (3, i), (3, i), color)

                
                tabla_registros_pdf.setStyle(estilo_tabla)

                elementos.append(tabla_registros_pdf)
                if contador_dias==3:
                    elementos.append(Spacer(1, 10))
                elif contador%3==0:
                    elementos.append(Spacer(1, 20))
                else:
                    elementos.append(Spacer(1, 30))
        else:
            elementos.append(Paragraph("Sin sesiones registradas para esta semana"))
        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer


    def generar_reporte_de_sesiones_por_mes_pdf(nombre_usuario, fecha):

        

        margin_left = 0.6 * inch
        margin_right = 0.6 * inch
        margin_top = 1.2 * inch  # Deja espacio para el carimbo
        margin_bottom = 1 * inch

        rojo_fuerte = colors.Color(1, 0.298, 0.298)      # #FF4C4C
        naranja_suave = colors.Color(1, 0.835, 0.502)    # #FFD580
        amarillo_claro = colors.Color(1, 1, 0.6)         # #FFFF99
        verde_claro = colors.Color(0.698, 0.949, 0.698)  # #B2F2B2

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter, 
                            leftMargin=margin_left,
                            rightMargin=margin_right,
                            topMargin=margin_top,
                            bottomMargin=margin_bottom)
        elementos = []

        

        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('Titulo', fontSize=16, alignment=1, fontName="Helvetica-Bold", underline=True)
        estilo_subtitulo_2 = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  
        estilo_subtitulo_3 = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  
        estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=6, alignment=0) 
        estilo_datos = estilos['Normal']
        estilo_centrado_grande = ParagraphStyle('Centrado', fontSize=30, alignment=0)

        

        #logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
        #logo_direccion = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 0.8 * inch, 0.8 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo_2)


        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.2 * inch), height - (0.2 * inch) - imagen_logo.drawHeight)
            titulo_x = width / 2  
            titulo_y = height - (0.7 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x - 90, titulo_y, f"Informe de Sesiones")
            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        #elementos.append(Spacer(1, 20))

        ano_obj = str(fecha).split('-')[0]
        mes_obj = str(fecha).split('-')[1]

        fecha_inicio = date(int(ano_obj), int(mes_obj), 1)

        fecha_final = date(int(ano_obj), int(mes_obj)+1, 1)

        if int(mes_obj) == 12:
            fecha_final = date(int(ano_obj) + 1, 1, 1)

        fecha_objetivo = datetime.strptime(fecha, "%Y-%m-%d")

        fecha_date = fecha_objetivo.date()

        dias_al_lunes = fecha_date.weekday()

        fecha_lunes = fecha_date - timedelta(days=dias_al_lunes)
        fecha_sabado = fecha_lunes + timedelta(days=5)

        sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.fecha>=fecha_inicio, Sesion.fecha<fecha_final).order_by(Sesion.fecha, Sesion.hora).all()


        dia_primero = fecha_inicio.strftime("%Y-%m-%d")
        if sesiones:
            contador = 0
            for sesion in sesiones:
                dia_sesion_ing = sesion.fecha.strftime("%Y-%m-%d")
                dia_primero = dia_sesion_ing
                contador = contador + 1
                if contador == 1:
                    break

        if sesiones:
            contador_hojas = 0
            contador = 0
            contador_dias = 0
            buffer_dias = dia_primero
            for sesion in sesiones:
                id_sesion = sesion.id_sesion

                dia_sesion_ing = sesion.fecha.strftime("%A")
                fecha_str = sesion.fecha.strftime("%d/%m/%Y")
                fecha_str_ob = sesion.fecha.strftime("%Y-%m-%d")
                

                if buffer_dias != fecha_str_ob:
                    contador_dias = 0
                    contador = 0

                if contador_dias == 0:
                    if contador_hojas >0:
                        elementos.append(PageBreak())
                    elementos.append(Paragraph(f"{DIAS_INGLES[dia_sesion_ing]}, {fecha_str}", estilo_titulo))
                    elementos.append(Spacer(1, 10))
                    buffer_dias = fecha_str_ob
                elif contador%3==0:
                    elementos.append(PageBreak())

                contador_dias = contador_dias + 1
                contador = contador + 1
                contador_hojas = contador_hojas + 1
                
                
                detalles = db.session.query(Estudiante, DetalleSesion).join(DetalleSesion, DetalleSesion.id_estudiante==Estudiante.id_estudiante).filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
                #detalles = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
                docente = Docente.query.get(sesion.id_docente)
                color_docente = hex_to_color(docente.color)
                
                

                cabecera = [Paragraph("Hora", estilo_subtitulo_3), Paragraph(f"{sesion.seccion} {sesion.nivel}", estilo_subtitulo_3), '', '', Paragraph(f"<b>Teacher:</b> {docente.nombres} {docente.apellidos}", estilo_subtitulo_3), '', '']
                segunda_cabecera = [f"{sesion.hora.strftime('%H:%M')}", Paragraph(f"N°", estilo_subtitulo), Paragraph(f"Estudiantes", estilo_subtitulo_3), '', Paragraph(f"Show / No Show", estilo_subtitulo), Paragraph(f"Total Students", estilo_subtitulo), Paragraph(f"Foto", estilo_subtitulo_3)]
                tabla_registros = []
                tabla_registros.append(cabecera)
                tabla_registros.append(segunda_cabecera)
                for i in range(0,10, 1):
                    fila = ['', str(i+1), '', '', '', '', '']
                    tabla_registros.append(fila)
                

                estudiantes_totales = 0
                estudiantes_asistio = 0
                
                ind = 2
                if detalles:
                    for estudiante, detalle in detalles:
                        tabla_registros[ind][2] = Paragraph(f"{estudiante.nombres} {estudiante.apellidos}", estilo_subtitulo)
                        
                        tabla_registros[ind][4] = Paragraph(f"{detalle.nivel_seccion}", estilo_subtitulo)
                        
                        if detalle.estado_registro == 'Asistio':
                            tabla_registros[ind][3] = detalle.calificacion
                            estudiantes_totales = estudiantes_totales + 1
                            estudiantes_asistio = estudiantes_asistio + 1
                        elif detalle.estado_registro == 'Falto':
                            tabla_registros[ind][3] = "Falto"
                            estudiantes_totales = estudiantes_totales + 1
                        elif detalle.estado_registro == 'Cancelado':
                            tabla_registros[ind][3] = "Cancelo"
                        
                        ind = ind + 1
                
                imagen_clase = ''
                if sesion.imagen_url:
                    #ruta_imagen = os.path.join(os.getcwd(), 'app', 'static', str(sesion.imagen_url))
                    ruta_imagen = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', str(sesion.imagen_url))
                    imagen_clase = Image(ruta_imagen)
                    imagen_width = imagen_clase.drawWidth
                    imagen_height = imagen_clase.drawHeight

                    # Definir el tamaño máximo de la celda
                    celda_width = 1.6 * inch  # Ancho máximo de la celda que contiene la imagen
                    celda_height = 1.6 * inch  # Alto máximo de la celda que contiene la imagen

                    # Ajustar el tamaño de la imagen para que no se deforme
                    imagen_width = min(imagen_width, celda_width)
                    imagen_height = min(imagen_height, celda_height)
                    imagen_clase.drawWidth = imagen_width
                    imagen_clase.drawHeight = imagen_height

                # Definir los anchos de las columnas
                col_widths = [ 0.7 * inch,  0.3 * inch, 2 * inch, 0.3*inch, 0.8 * inch, 0.8 * inch, 1.8*inch]  # Ancho de cada columna
                        
                tabla_registros[2][6] = imagen_clase
                tabla_registros[2][5] = Paragraph(f"<b>{estudiantes_asistio}/{estudiantes_totales}</b>", estilo_titulo)
                





                tabla_registros_pdf = Table(tabla_registros, colWidths=col_widths, rowHeights=0.2*inch)

                estilo_tabla = TableStyle([('BACKGROUND', (0, 0), (-1, 1), color_docente),
                                        ('BACKGROUND', (0, 0), (0, -1), color_docente),
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                                        ('FONTSIZE', (1, 0), (-1, -1), 6),
                                        ('FONTSIZE', (0, 1), (0, -1), 15),
                                        ('SPAN', (1, 0), (3, 0)),
                                        ('SPAN', (2, 1), (3, 1)),
                                        ('SPAN', (4, 0), (-1, 0)),
                                        ('SPAN', (0, 1), (0, -1)),
                                        ('SPAN', (-1, 2), (-1, -1)),
                                        ('SPAN', (5, 2), (5, -1)),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
                                        ('VALIGN', (5, 2), (5, -1), 'MIDDLE'),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])
                
                for i in range(2, 11, 1):
                    calificacion = tabla_registros[i][3]
                    if calificacion == '':
                        continue
                    if calificacion == 'Falto' or calificacion == 'Cancelo':
                        color = naranja_suave
                    elif float(calificacion)>=85.0:
                        color = verde_claro
                    elif float(calificacion)<85.0:
                        color = amarillo_claro
                    estilo_tabla.add("BACKGROUND", (3, i), (3, i), color)

                
                tabla_registros_pdf.setStyle(estilo_tabla)

                elementos.append(tabla_registros_pdf)
                
                if contador%3==0:
                    elementos.append(Spacer(1, 5))
                else:
                    elementos.append(Spacer(1, 30))
        else:
            elementos.append(Paragraph("Sin sesiones registradas para esta semana"))
        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer
    

    # ----------------------------------------------------------------------------------------------------------------------------
    # -------------------------------------------- REPORTES SESIONES POR DOCENTE -------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------------

    
    def generar_reporte_de_sesiones_por_dia_docente_pdf(nombre_usuario, fecha, id_docente):
        
        margin_left = 0.6 * inch
        margin_right = 0.6 * inch
        margin_top = 1.2 * inch  # Deja espacio para el carimbo
        margin_bottom = 1 * inch

        rojo_fuerte = colors.Color(1, 0.298, 0.298)      # #FF4C4C
        naranja_suave = colors.Color(1, 0.835, 0.502)    # #FFD580
        amarillo_claro = colors.Color(1, 1, 0.6)         # #FFFF99
        verde_claro = colors.Color(0.698, 0.949, 0.698)  # #B2F2B2

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter, 
                            leftMargin=margin_left,
                            rightMargin=margin_right,
                            topMargin=margin_top,
                            bottomMargin=margin_bottom)
        elementos = []

        

        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('Titulo', fontSize=16, alignment=1, fontName="Helvetica-Bold", underline=True)
        estilo_subtitulo_2 = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  
        estilo_subtitulo_3 = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  
        estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=6, alignment=0) 
        estilo_datos = estilos['Normal']
        estilo_centrado_grande = ParagraphStyle('Centrado', fontSize=30, alignment=0)

        

        #logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
        #logo_direccion = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 0.8 * inch, 0.8 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo_2)


        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.2 * inch), height - (0.2 * inch) - imagen_logo.drawHeight)
            titulo_x = width / 2  
            titulo_y = height - (0.7 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x - 150, titulo_y, f"Informe de Sesiones del {fecha}")
            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        #elementos.append(Spacer(1, 20))

        fecha_objetivo = datetime.strptime(fecha, "%Y-%m-%d")
        sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.id_docente == id_docente, Sesion.fecha==fecha_objetivo).order_by(Sesion.fecha, Sesion.hora).all()

        if sesiones:
            contador = 0
            for sesion in sesiones:
                id_sesion = sesion.id_sesion
                contador = contador + 1
                
                
                detalles = db.session.query(Estudiante, DetalleSesion).join(DetalleSesion, DetalleSesion.id_estudiante==Estudiante.id_estudiante).filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
                #detalles = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
                docente = Docente.query.get(sesion.id_docente)
                color_docente = hex_to_color(docente.color)
                
                

                cabecera = [Paragraph("Hora", estilo_subtitulo_2), Paragraph(f"{sesion.seccion} {sesion.nivel}", estilo_subtitulo_2), '', '', Paragraph(f"<b>Teacher:</b> {docente.nombres} {docente.apellidos}", estilo_subtitulo_2), '', '']
                segunda_cabecera = [f"{sesion.hora.strftime('%H:%M')}", Paragraph(f"N°", estilo_subtitulo), Paragraph(f"Estudiantes", estilo_subtitulo_2), '', Paragraph(f"Show / No Show", estilo_subtitulo), Paragraph(f"Total Students", estilo_subtitulo), Paragraph(f"Foto", estilo_subtitulo_2)]
                tabla_registros = []
                tabla_registros.append(cabecera)
                tabla_registros.append(segunda_cabecera)
                for i in range(0,10, 1):
                    fila = ['', str(i+1), '', '', '', '', '']
                    tabla_registros.append(fila)
                

                estudiantes_totales = 0
                estudiantes_asistio = 0
                
                ind = 2
                if detalles:
                    for estudiante, detalle in detalles:
                        tabla_registros[ind][2] = Paragraph(f"{estudiante.nombres} {estudiante.apellidos}", estilo_subtitulo)
                        
                        tabla_registros[ind][4] = Paragraph(f"{detalle.nivel_seccion}", estilo_subtitulo)
                        
                        if detalle.estado_registro == 'Asistio':
                            tabla_registros[ind][3] = detalle.calificacion
                            estudiantes_totales = estudiantes_totales + 1
                            estudiantes_asistio = estudiantes_asistio + 1
                        elif detalle.estado_registro == 'Falto':
                            tabla_registros[ind][3] = "Falto"
                            estudiantes_totales = estudiantes_totales + 1
                        elif detalle.estado_registro == 'Cancelado':
                            tabla_registros[ind][3] = "Cancelo"
                        ind = ind + 1
                
                imagen_clase = ''
                if sesion.imagen_url:
                    #ruta_imagen = os.path.join(os.getcwd(), 'app', 'static', str(sesion.imagen_url))
                    ruta_imagen = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', str(sesion.imagen_url))
                    imagen_clase = Image(ruta_imagen)
                    imagen_width = imagen_clase.drawWidth
                    imagen_height = imagen_clase.drawHeight

                    # Definir el tamaño máximo de la celda
                    celda_width = 1.6 * inch  # Ancho máximo de la celda que contiene la imagen
                    celda_height = 1.6 * inch  # Alto máximo de la celda que contiene la imagen

                    # Ajustar el tamaño de la imagen para que no se deforme
                    imagen_width = min(imagen_width, celda_width)
                    imagen_height = min(imagen_height, celda_height)
                    imagen_clase.drawWidth = imagen_width
                    imagen_clase.drawHeight = imagen_height

                # Definir los anchos de las columnas
                col_widths = [ 0.7 * inch,  0.3 * inch, 2 * inch, 0.3*inch, 0.8 * inch, 0.8 * inch, 1.8*inch]  # Ancho de cada columna
                        
                tabla_registros[2][6] = imagen_clase
                tabla_registros[2][5] = Paragraph(f"<b>{estudiantes_asistio}/{estudiantes_totales}</b>", estilo_titulo)
                





                tabla_registros_pdf = Table(tabla_registros, colWidths=col_widths, rowHeights=0.2*inch)

                estilo_tabla = TableStyle([('BACKGROUND', (0, 0), (-1, 1), color_docente),
                                        ('BACKGROUND', (0, 0), (0, -1), color_docente),
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                                        ('FONTSIZE', (1, 0), (-1, -1), 6),
                                        ('FONTSIZE', (0, 1), (0, -1), 15),
                                        ('SPAN', (1, 0), (3, 0)),
                                        ('SPAN', (2, 1), (3, 1)),
                                        ('SPAN', (4, 0), (-1, 0)),
                                        ('SPAN', (0, 1), (0, -1)),
                                        ('SPAN', (-1, 2), (-1, -1)),
                                        ('SPAN', (5, 2), (5, -1)),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
                                        ('VALIGN', (5, 2), (5, -1), 'MIDDLE'),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])
                
                for i in range(2, 11, 1):
                    calificacion = tabla_registros[i][3]
                    if calificacion == '':
                        continue
                    if calificacion == 'Falto' or calificacion == 'Cancelo':
                        color = naranja_suave
                    elif float(calificacion)>=85.0:
                        color = verde_claro
                    elif float(calificacion)<85.0:
                        color = amarillo_claro
                    estilo_tabla.add("BACKGROUND", (3, i), (3, i), color)

                
                tabla_registros_pdf.setStyle(estilo_tabla)

                elementos.append(tabla_registros_pdf)
                if contador%3==0:

                    elementos.append(Spacer(1, 20))
                else:
                    elementos.append(Spacer(1, 40))
        else:
            elementos.append(Paragraph("Sin sesiones registradas para esta fecha"))
        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer

    
    def generar_reporte_de_sesiones_por_semana_docente_pdf(nombre_usuario, fecha, id_docente):

        

        margin_left = 0.6 * inch
        margin_right = 0.6 * inch
        margin_top = 1.2 * inch  # Deja espacio para el carimbo
        margin_bottom = 1 * inch

        rojo_fuerte = colors.Color(1, 0.298, 0.298)      # #FF4C4C
        naranja_suave = colors.Color(1, 0.835, 0.502)    # #FFD580
        amarillo_claro = colors.Color(1, 1, 0.6)         # #FFFF99
        verde_claro = colors.Color(0.698, 0.949, 0.698)  # #B2F2B2

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter, 
                            leftMargin=margin_left,
                            rightMargin=margin_right,
                            topMargin=margin_top,
                            bottomMargin=margin_bottom)
        elementos = []

        

        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('Titulo', fontSize=16, alignment=1, fontName="Helvetica-Bold", underline=True)
        estilo_subtitulo_2 = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  
        estilo_subtitulo_3 = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  
        estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=6, alignment=0) 
        estilo_datos = estilos['Normal']
        estilo_centrado_grande = ParagraphStyle('Centrado', fontSize=30, alignment=0)

        

        #logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
        #logo_direccion = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 0.8 * inch, 0.8 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo_2)


        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.2 * inch), height - (0.2 * inch) - imagen_logo.drawHeight)
            titulo_x = width / 2  
            titulo_y = height - (0.7 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x - 90, titulo_y, f"Informe de Sesiones")
            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        #elementos.append(Spacer(1, 20))

        fecha_objetivo = datetime.strptime(fecha, "%Y-%m-%d")

        fecha_date = fecha_objetivo.date()

        dias_al_lunes = fecha_date.weekday()

        fecha_lunes = fecha_date - timedelta(days=dias_al_lunes)
        fecha_sabado = fecha_lunes + timedelta(days=5)

        sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.id_docente == id_docente, Sesion.fecha>=fecha_lunes, Sesion.fecha<=fecha_sabado).order_by(Sesion.fecha, Sesion.hora).all()

        dia_primero = 'Lunes'
        if sesiones:
            contador = 0
            for sesion in sesiones:
                dia_sesion_ing = sesion.fecha.strftime("%A")
                dia_primero = DIAS_INGLES[dia_sesion_ing]
                contador = contador + 1
                if contador == 1:
                    break

        if sesiones:
            contador_hojas = 0
            contador = 0
            contador_dias = 0
            buffer_dias = dia_primero
            for sesion in sesiones:
                id_sesion = sesion.id_sesion

                dia_sesion_ing = sesion.fecha.strftime("%A")
                fecha_str = sesion.fecha.strftime("%d/%m/%Y")
                

                if buffer_dias != DIAS_INGLES[dia_sesion_ing]:
                    contador_dias = 0
                    contador = 0

                if contador_dias == 0:
                    if contador_hojas >0:
                        elementos.append(PageBreak())
                    elementos.append(Paragraph(f"{DIAS_INGLES[dia_sesion_ing]}, {fecha_str}", estilo_titulo))
                    elementos.append(Spacer(1, 10))
                    buffer_dias = DIAS_INGLES[dia_sesion_ing]

                contador_dias = contador_dias + 1
                contador = contador + 1
                contador_hojas = contador_hojas + 1
                
                
                detalles = db.session.query(Estudiante, DetalleSesion).join(DetalleSesion, DetalleSesion.id_estudiante==Estudiante.id_estudiante).filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
                #detalles = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
                docente = Docente.query.get(sesion.id_docente)
                color_docente = hex_to_color(docente.color)
                
                

                cabecera = [Paragraph("Hora", estilo_subtitulo_3), Paragraph(f"{sesion.seccion} {sesion.nivel}", estilo_subtitulo_3), '', '', Paragraph(f"<b>Teacher:</b> {docente.nombres} {docente.apellidos}", estilo_subtitulo_3), '', '']
                segunda_cabecera = [f"{sesion.hora.strftime('%H:%M')}", Paragraph(f"N°", estilo_subtitulo), Paragraph(f"Estudiantes", estilo_subtitulo_3), '', Paragraph(f"Show / No Show", estilo_subtitulo), Paragraph(f"Total Students", estilo_subtitulo), Paragraph(f"Foto", estilo_subtitulo_3)]
                tabla_registros = []
                tabla_registros.append(cabecera)
                tabla_registros.append(segunda_cabecera)
                for i in range(0,10, 1):
                    fila = ['', str(i+1), '', '', '', '', '']
                    tabla_registros.append(fila)
                

                estudiantes_totales = 0
                estudiantes_asistio = 0
                
                ind = 2
                if detalles:
                    for estudiante, detalle in detalles:
                        tabla_registros[ind][2] = Paragraph(f"{estudiante.nombres} {estudiante.apellidos}", estilo_subtitulo)
                        
                        tabla_registros[ind][4] = Paragraph(f"{detalle.nivel_seccion}", estilo_subtitulo)
                        
                        if detalle.estado_registro == 'Asistio':
                            tabla_registros[ind][3] = detalle.calificacion
                            estudiantes_totales = estudiantes_totales + 1
                            estudiantes_asistio = estudiantes_asistio + 1
                        elif detalle.estado_registro == 'Falto':
                            tabla_registros[ind][3] = "Falto"
                            estudiantes_totales = estudiantes_totales + 1
                        elif detalle.estado_registro == 'Cancelado':
                            tabla_registros[ind][3] = "Cancelo"
                        ind = ind + 1
                
                imagen_clase = ''
                if sesion.imagen_url:
                    #ruta_imagen = os.path.join(os.getcwd(), 'app', 'static', str(sesion.imagen_url))
                    ruta_imagen = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', str(sesion.imagen_url))
                    imagen_clase = Image(ruta_imagen)
                    imagen_width = imagen_clase.drawWidth
                    imagen_height = imagen_clase.drawHeight

                    # Definir el tamaño máximo de la celda
                    celda_width = 1.6 * inch  # Ancho máximo de la celda que contiene la imagen
                    celda_height = 1.6 * inch  # Alto máximo de la celda que contiene la imagen

                    # Ajustar el tamaño de la imagen para que no se deforme
                    imagen_width = min(imagen_width, celda_width)
                    imagen_height = min(imagen_height, celda_height)
                    imagen_clase.drawWidth = imagen_width
                    imagen_clase.drawHeight = imagen_height

                # Definir los anchos de las columnas
                col_widths = [ 0.7 * inch,  0.3 * inch, 2 * inch, 0.3*inch, 0.8 * inch, 0.8 * inch, 1.8*inch]  # Ancho de cada columna
                        
                tabla_registros[2][6] = imagen_clase
                tabla_registros[2][5] = Paragraph(f"<b>{estudiantes_asistio}/{estudiantes_totales}</b>", estilo_titulo)
                





                tabla_registros_pdf = Table(tabla_registros, colWidths=col_widths, rowHeights=0.2*inch)

                estilo_tabla = TableStyle([('BACKGROUND', (0, 0), (-1, 1), color_docente),
                                        ('BACKGROUND', (0, 0), (0, -1), color_docente),
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                                        ('FONTSIZE', (1, 0), (-1, -1), 6),
                                        ('FONTSIZE', (0, 1), (0, -1), 15),
                                        ('SPAN', (1, 0), (3, 0)),
                                        ('SPAN', (2, 1), (3, 1)),
                                        ('SPAN', (4, 0), (-1, 0)),
                                        ('SPAN', (0, 1), (0, -1)),
                                        ('SPAN', (-1, 2), (-1, -1)),
                                        ('SPAN', (5, 2), (5, -1)),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
                                        ('VALIGN', (5, 2), (5, -1), 'MIDDLE'),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])
                
                for i in range(2, 11, 1):
                    calificacion = tabla_registros[i][3]
                    if calificacion == '':
                        continue
                    if calificacion == 'Falto' or calificacion == 'Cancelo':
                        color = naranja_suave
                    elif float(calificacion)>=85.0:
                        color = verde_claro
                    elif float(calificacion)<85.0:
                        color = amarillo_claro
                    estilo_tabla.add("BACKGROUND", (3, i), (3, i), color)

                
                tabla_registros_pdf.setStyle(estilo_tabla)

                elementos.append(tabla_registros_pdf)
                if contador_dias==3:
                    elementos.append(Spacer(1, 10))
                elif contador%3==0:
                    elementos.append(Spacer(1, 20))
                else:
                    elementos.append(Spacer(1, 30))
        else:
            elementos.append(Paragraph("Sin sesiones registradas para esta semana"))
        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer


    def generar_reporte_de_sesiones_por_mes_docente_pdf(nombre_usuario, fecha, id_docente):

        

        margin_left = 0.6 * inch
        margin_right = 0.6 * inch
        margin_top = 1.2 * inch  # Deja espacio para el carimbo
        margin_bottom = 1 * inch

        rojo_fuerte = colors.Color(1, 0.298, 0.298)      # #FF4C4C
        naranja_suave = colors.Color(1, 0.835, 0.502)    # #FFD580
        amarillo_claro = colors.Color(1, 1, 0.6)         # #FFFF99
        verde_claro = colors.Color(0.698, 0.949, 0.698)  # #B2F2B2

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter, 
                            leftMargin=margin_left,
                            rightMargin=margin_right,
                            topMargin=margin_top,
                            bottomMargin=margin_bottom)
        elementos = []

        

        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('Titulo', fontSize=16, alignment=1, fontName="Helvetica-Bold", underline=True)
        estilo_subtitulo_2 = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  
        estilo_subtitulo_3 = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  
        estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=6, alignment=0) 
        estilo_datos = estilos['Normal']
        estilo_centrado_grande = ParagraphStyle('Centrado', fontSize=30, alignment=0)

        

        #logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
        #logo_direccion = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 0.8 * inch, 0.8 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo_2)


        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.2 * inch), height - (0.2 * inch) - imagen_logo.drawHeight)
            titulo_x = width / 2  
            titulo_y = height - (0.7 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x - 90, titulo_y, f"Informe de Sesiones")
            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        #elementos.append(Spacer(1, 20))

        ano_obj = str(fecha).split('-')[0]
        mes_obj = str(fecha).split('-')[1]

        fecha_inicio = date(int(ano_obj), int(mes_obj), 1)

        fecha_final = date(int(ano_obj), int(mes_obj)+1, 1)

        if int(mes_obj) == 12:
            fecha_final = date(int(ano_obj) + 1, 1, 1)

        fecha_objetivo = datetime.strptime(fecha, "%Y-%m-%d")

        fecha_date = fecha_objetivo.date()

        dias_al_lunes = fecha_date.weekday()

        fecha_lunes = fecha_date - timedelta(days=dias_al_lunes)
        fecha_sabado = fecha_lunes + timedelta(days=5)

        sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.id_docente == id_docente, Sesion.fecha>=fecha_inicio, Sesion.fecha<fecha_final).order_by(Sesion.fecha, Sesion.hora).all()


        dia_primero = fecha_inicio.strftime("%Y-%m-%d")
        if sesiones:
            contador = 0
            for sesion in sesiones:
                dia_sesion_ing = sesion.fecha.strftime("%Y-%m-%d")
                dia_primero = dia_sesion_ing
                contador = contador + 1
                if contador == 1:
                    break

        if sesiones:
            contador_hojas = 0
            contador = 0
            contador_dias = 0
            buffer_dias = dia_primero
            for sesion in sesiones:
                id_sesion = sesion.id_sesion

                dia_sesion_ing = sesion.fecha.strftime("%A")
                fecha_str = sesion.fecha.strftime("%d/%m/%Y")
                fecha_str_ob = sesion.fecha.strftime("%Y-%m-%d")
                

                if buffer_dias != fecha_str_ob:
                    contador_dias = 0
                    contador = 0

                if contador_dias == 0:
                    if contador_hojas >0:
                        elementos.append(PageBreak())
                    elementos.append(Paragraph(f"{DIAS_INGLES[dia_sesion_ing]}, {fecha_str}", estilo_titulo))
                    elementos.append(Spacer(1, 10))
                    buffer_dias = fecha_str_ob
                elif contador%3==0:
                    elementos.append(PageBreak())

                contador_dias = contador_dias + 1
                contador = contador + 1
                contador_hojas = contador_hojas + 1
                
                
                detalles = db.session.query(Estudiante, DetalleSesion).join(DetalleSesion, DetalleSesion.id_estudiante==Estudiante.id_estudiante).filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
                #detalles = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion).all()
                docente = Docente.query.get(sesion.id_docente)
                color_docente = hex_to_color(docente.color)
                
                

                cabecera = [Paragraph("Hora", estilo_subtitulo_3), Paragraph(f"{sesion.seccion} {sesion.nivel}", estilo_subtitulo_3), '', '', Paragraph(f"<b>Teacher:</b> {docente.nombres} {docente.apellidos}", estilo_subtitulo_3), '', '']
                segunda_cabecera = [f"{sesion.hora.strftime('%H:%M')}", Paragraph(f"N°", estilo_subtitulo), Paragraph(f"Estudiantes", estilo_subtitulo_3), '', Paragraph(f"Show / No Show", estilo_subtitulo), Paragraph(f"Total Students", estilo_subtitulo), Paragraph(f"Foto", estilo_subtitulo_3)]
                tabla_registros = []
                tabla_registros.append(cabecera)
                tabla_registros.append(segunda_cabecera)
                for i in range(0,10, 1):
                    fila = ['', str(i+1), '', '', '', '', '']
                    tabla_registros.append(fila)
                

                estudiantes_totales = 0
                estudiantes_asistio = 0
                
                ind = 2
                if detalles:
                    for estudiante, detalle in detalles:
                        tabla_registros[ind][2] = Paragraph(f"{estudiante.nombres} {estudiante.apellidos}", estilo_subtitulo)
                        
                        tabla_registros[ind][4] = Paragraph(f"{detalle.nivel_seccion}", estilo_subtitulo)
                        
                        if detalle.estado_registro == 'Asistio':
                            tabla_registros[ind][3] = detalle.calificacion
                            estudiantes_totales = estudiantes_totales + 1
                            estudiantes_asistio = estudiantes_asistio + 1
                        elif detalle.estado_registro == 'Falto':
                            tabla_registros[ind][3] = "Falto"
                            estudiantes_totales = estudiantes_totales + 1
                        elif detalle.estado_registro == 'Cancelado':
                            tabla_registros[ind][3] = "Cancelo"
                        
                        ind = ind + 1
                
                imagen_clase = ''
                if sesion.imagen_url:
                    #ruta_imagen = os.path.join(os.getcwd(), 'app', 'static', str(sesion.imagen_url))
                    ruta_imagen = os.path.join('var', 'www', 'okaprendeingles', 'app', 'static', str(sesion.imagen_url))
                    imagen_clase = Image(ruta_imagen)
                    imagen_width = imagen_clase.drawWidth
                    imagen_height = imagen_clase.drawHeight

                    # Definir el tamaño máximo de la celda
                    celda_width = 1.6 * inch  # Ancho máximo de la celda que contiene la imagen
                    celda_height = 1.6 * inch  # Alto máximo de la celda que contiene la imagen

                    # Ajustar el tamaño de la imagen para que no se deforme
                    imagen_width = min(imagen_width, celda_width)
                    imagen_height = min(imagen_height, celda_height)
                    imagen_clase.drawWidth = imagen_width
                    imagen_clase.drawHeight = imagen_height

                # Definir los anchos de las columnas
                col_widths = [ 0.7 * inch,  0.3 * inch, 2 * inch, 0.3*inch, 0.8 * inch, 0.8 * inch, 1.8*inch]  # Ancho de cada columna
                        
                tabla_registros[2][6] = imagen_clase
                tabla_registros[2][5] = Paragraph(f"<b>{estudiantes_asistio}/{estudiantes_totales}</b>", estilo_titulo)
                





                tabla_registros_pdf = Table(tabla_registros, colWidths=col_widths, rowHeights=0.2*inch)

                estilo_tabla = TableStyle([('BACKGROUND', (0, 0), (-1, 1), color_docente),
                                        ('BACKGROUND', (0, 0), (0, -1), color_docente),
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        #('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                                        ('FONTSIZE', (1, 0), (-1, -1), 6),
                                        ('FONTSIZE', (0, 1), (0, -1), 15),
                                        ('SPAN', (1, 0), (3, 0)),
                                        ('SPAN', (2, 1), (3, 1)),
                                        ('SPAN', (4, 0), (-1, 0)),
                                        ('SPAN', (0, 1), (0, -1)),
                                        ('SPAN', (-1, 2), (-1, -1)),
                                        ('SPAN', (5, 2), (5, -1)),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
                                        ('VALIGN', (5, 2), (5, -1), 'MIDDLE'),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])
                
                for i in range(2, 11, 1):
                    calificacion = tabla_registros[i][3]
                    if calificacion == '':
                        continue
                    if calificacion == 'Falto' or calificacion == 'Cancelo':
                        color = naranja_suave
                    elif float(calificacion)>=85.0:
                        color = verde_claro
                    elif float(calificacion)<85.0:
                        color = amarillo_claro
                    estilo_tabla.add("BACKGROUND", (3, i), (3, i), color)

                
                tabla_registros_pdf.setStyle(estilo_tabla)

                elementos.append(tabla_registros_pdf)
                
                if contador%3==0:
                    elementos.append(Spacer(1, 5))
                else:
                    elementos.append(Spacer(1, 30))
        else:
            elementos.append(Paragraph("Sin sesiones registradas para esta semana"))
        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer