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
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
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

MES_INGLES = {
    "January": "Enero",
    "February": "Febrero",
    "March": "Marzo",
    "April": "Abril",
    "May": "Mayo",
    "June": "Junio",
    "July": "Julio",
    "August": "Agosto",
    "September": "Septiembre",
    "October": "Octubre",
    "November": "Noviembre",
    "December": "Diciembre",
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
logo_direccion = os.path.join('var', 'www', 'OkAprendeIngles', 'app', 'static', 'img', 'logo.jpeg')

class ServiciosReportesInformes():

    def generar_informe_mensual_estudiantes_pdf(nombre_usuario, fecha):

        
        


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
        #logo_direccion = os.path.join('var', 'www', 'OkAprendeIngles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 0.8 * inch, 0.8 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ano_actual = datetime.now().strftime("%Y")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo_2)


        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.2 * inch), height - (0.2 * inch) - imagen_logo.drawHeight)

            titulo_x = width / 2  
            titulo_y = height - (0.5 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x + 130, titulo_y, f"NOTA INTERNA")

            titulo_x = width / 2  
            titulo_y = height - (0.7 * inch) 
            canvas.setFont("Helvetica-Bold", 11)
            canvas.drawString(titulo_x + 210, titulo_y, f"D.T. /{ano_actual}")

            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        #elementos.append(Spacer(1, 20))

        fecha_objetivo = datetime.strptime(fecha, "%Y-%m-%d")

        mes_actual = fecha_objetivo.date()
        mes_actual = mes_actual.replace(day=1)

        fecha_no_expirados = fecha_objetivo + relativedelta(months=1)
        fecha_depurados_inicio = fecha_objetivo - relativedelta(months=5)
        fecha_expirados_inicio = fecha_objetivo - relativedelta(months=2)

        fecha_no_expirados = fecha_no_expirados.date()
        fecha_no_expirados = fecha_no_expirados.replace(day=1)

        fecha_depurados_inicio = fecha_depurados_inicio.date()
        fecha_depurados_inicio = fecha_depurados_inicio.replace(day=1)

        fecha_depurados_dos = fecha_depurados_inicio + relativedelta(months=1)
        fecha_depurados_tres = fecha_depurados_inicio + relativedelta(months=2)

        mes_depurado_uno = MES_INGLES[fecha_depurados_inicio.strftime("%B")]
        mes_depurado_dos = MES_INGLES[fecha_depurados_dos.strftime("%B")]
        mes_depurado_tres = MES_INGLES[fecha_depurados_tres.strftime("%B")]

        fecha_expirados_inicio = fecha_expirados_inicio.date()
        fecha_expirados_inicio = fecha_expirados_inicio.replace(day=1)

        fecha_actual = datetime.now()

        
        cantidad_estudiantes_no_expirados_basico = Estudiante.query.filter(Estudiante.fin_contrato>=fecha_no_expirados, Estudiante.nombre_nivel=='Basico').count()
        cantidad_estudiantes_no_expirados_intermedio = Estudiante.query.filter(Estudiante.fin_contrato>=fecha_no_expirados, Estudiante.nombre_nivel=='Intermedio').count()
        cantidad_estudiantes_no_expirados_avanzado = Estudiante.query.filter(Estudiante.fin_contrato>=fecha_no_expirados, Estudiante.nombre_nivel=='Avanzado').count()

        cantidad_estudiantes_expirados_basico = Estudiante.query.filter(Estudiante.fin_contrato>=fecha_expirados_inicio, Estudiante.fin_contrato<fecha_no_expirados, Estudiante.nombre_nivel=='Basico').count()
        cantidad_estudiantes_expirados_intermedio = Estudiante.query.filter(Estudiante.fin_contrato>=fecha_expirados_inicio, Estudiante.fin_contrato<fecha_no_expirados, Estudiante.nombre_nivel=='Intermedio').count()
        cantidad_estudiantes_expirados_avanzado = Estudiante.query.filter(Estudiante.fin_contrato>=fecha_expirados_inicio, Estudiante.fin_contrato<fecha_no_expirados, Estudiante.nombre_nivel=='Avanzado').count()

        cantidad_estudiantes_depurados_basico = Estudiante.query.filter(Estudiante.fin_contrato>=fecha_depurados_inicio, Estudiante.fin_contrato<fecha_expirados_inicio, Estudiante.nombre_nivel=='Basico').count()
        cantidad_estudiantes_depurados_intermedio = Estudiante.query.filter(Estudiante.fin_contrato>=fecha_depurados_inicio, Estudiante.fin_contrato<fecha_expirados_inicio, Estudiante.nombre_nivel=='Intermedio').count()
        cantidad_estudiantes_depurados_avanzado = Estudiante.query.filter(Estudiante.fin_contrato>=fecha_depurados_inicio, Estudiante.fin_contrato<fecha_expirados_inicio, Estudiante.nombre_nivel=='Avanzado').count()

        total_no_expirados = cantidad_estudiantes_no_expirados_avanzado + cantidad_estudiantes_no_expirados_basico + cantidad_estudiantes_no_expirados_intermedio
        total_expirados = cantidad_estudiantes_expirados_avanzado + cantidad_estudiantes_expirados_basico + cantidad_estudiantes_expirados_intermedio
        total_depurados = cantidad_estudiantes_depurados_avanzado + cantidad_estudiantes_depurados_basico + cantidad_estudiantes_depurados_intermedio
        

        cantidad_estudiantes_nuevos = Estudiante.query.filter(Estudiante.inicio_contrato>=mes_actual, Estudiante.inicio_contrato<fecha_no_expirados).count()

        detalles_sesiones = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, DetalleSesion.id_sesion==Sesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.fecha>=mes_actual, Sesion.fecha<fecha_no_expirados, Sesion.seccion=='Test Oral', DetalleSesion.calificacion>=85, DetalleSesion.nivel_seccion==50).all()

        cantidad_estudiantes_concluidos = 0

        ids_estudiantes = []

        if detalles_sesiones:
            for sesion, detalle in detalles_sesiones:
                id_estudiante = detalle.id_estudiante
                if id_estudiante not in ids_estudiantes:
                    ids_estudiantes.append(id_estudiante)
                    estudiante = Estudiante.query.get(id_estudiante)
                    if(estudiante.speakout_completado==50 and estudiante.paso_examen==1):
                        cantidad_estudiantes_concluidos = cantidad_estudiantes_concluidos + 1
        
        fecha_actual_str = fecha_actual.strftime("%d/%m/%Y")
        mes_string = MES_INGLES[mes_actual.strftime("%B")]
        fecha_mes_str = mes_actual.strftime("%d/%m/%Y")
        ultimo_dia = fecha_no_expirados - timedelta(days=1)
        ultimo_dia_str = ultimo_dia.strftime("%d/%m/%Y")

        estilo_inicio = ParagraphStyle('Inicio', fontSize=8, alignment=0) 
        estilo_cuerpo = ParagraphStyle('Cuerpo', fontSize=8, alignment=1)

        ancho_columnas = [0.5*inch, 1*inch, 3*inch, 1*inch, 1*inch]

        tabla_datos = Table([
            [Paragraph(f"<b>PARA:</b>", estilo_inicio), '', Paragraph(f"<b>SR(A). ALEJANDRA BARRAGAN</b>", estilo_inicio), '', ''],
            ['', '', Paragraph(f"<b>DIRECTORA ADMINISTRATIVA</b>", estilo_inicio), '', ''],
            [Paragraph(f"<b>DE:</b>", estilo_inicio), '', Paragraph(f"<b>RECEPCIÓN</b>", estilo_inicio), '', ''],
            ['', '', '', '', ''],
            [Paragraph(f"<b>ASUNTO:</b>", estilo_inicio), '', Paragraph(f"<b>ENTREGA INFORME MENSUAL</b>", estilo_inicio), '', ''],
            [Paragraph(f"<b>FECHA:</b>", estilo_inicio), '', Paragraph(f"<b>{fecha_actual_str}</b>", estilo_inicio), '', ''],
            [Paragraph(f"Cordial saludo:", estilo_inicio), '', '', '', ''],
            [Paragraph(f"INFORME CARGA HORARIA MENSUAL DEL {fecha_mes_str} al {ultimo_dia_str}", estilo_cuerpo), '', Paragraph(f" Mediante la presente me dirijo a su persona para hacerle entrega de informe mensual correspondiente al mes de {mes_string} de {ano_actual} del Departamento Tutorial, el mismo que se detalla a continuación:", estilo_cuerpo), '', '']
        ], colWidths=ancho_columnas)

        estilo_tabla = TableStyle([
                                ('SPAN', (0, 0), (1, 0)),
                                ('SPAN', (2, 0), (-1, 0)),
                                ('SPAN', (0, 1), (1, 1)),
                                ('SPAN', (2, 1), (-1, 1)),
                                ('SPAN', (0, 2), (1, 2)),
                                ('SPAN', (2, 2), (-1, 2)),
                                ('SPAN', (0, 4), (1, 4)),
                                ('SPAN', (2, 4), (-1, 4)),
                                ('SPAN', (0, 5), (1, 5)),
                                ('SPAN', (2, 5), (-1, 5)),
                                ('SPAN', (0, 6), (1, 6)),
                                ('SPAN', (2, 6), (-1, 6)),
                                ('SPAN', (0, 7), (1, 7)),
                                ('SPAN', (2, 7), (-1, 7)),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
        
        tabla_datos.setStyle(estilo_tabla)

        elementos.append(tabla_datos)
        elementos.append(Spacer(1, 20))

        color_titulos_tabla = hex_to_color('#4472C4')

        estilo_tabla_datos_est = TableStyle([
                                ('SPAN', (1, 0), (2, 0)),
                                ('SPAN', (1, 1), (2, 1)),
                                ('SPAN', (1, 2), (2, 2)),
                                ('SPAN', (1, 3), (2, 3)),
                                ('SPAN', (1, 4), (2, 4)),
                                ('SPAN', (0, 5), (-1, 5)),
                                ('BACKGROUND', (0, 0), (-1, 0), color_titulos_tabla),
                                ('BACKGROUND', (0, 4), (-1, 4), color_titulos_tabla),
                                ('BACKGROUND', (0, 5), (-1, 5), colors.yellow),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
        
        estilo_tabla_datos_wel = TableStyle([
                                ('SPAN', (1, 0), (2, 0)),
                                ('SPAN', (1, 1), (2, 1)),
                                ('SPAN', (0, 2), (-1, 2)),
                                ('BACKGROUND', (0, 0), (-1, 0), color_titulos_tabla),
                                ('BACKGROUND', (0, 2), (-1, 2), colors.yellow),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
        
        estilo_tabla_datos_concluido = TableStyle([
                                ('SPAN', (1, 0), (2, 0)),
                                ('SPAN', (1, 1), (2, 1)),
                                ('BACKGROUND', (0, 0), (-1, 0), color_titulos_tabla),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])

        estilo_titulos_tabla = ParagraphStyle('titulo_tabla', fontSize=8, alignment=1, fontName="Helvetica-Bold", textColor=colors.white)
        estilo_cuerpo_tabla = ParagraphStyle('cuerpo_tabla', fontSize=8, alignment=0, textColor=colors.black)
        estilo_cantidad_tabla = ParagraphStyle('cantidad_tabla', fontSize=8, alignment=1, textColor=colors.black)

        tabla_no_expirados = Table([
            ['', Paragraph(f"DETALLE ESTUDIANTES NO EXPIRADOS", estilo_titulos_tabla), '', Paragraph(f"NÚMERO DE ESTUDIANTES", estilo_titulos_tabla), Paragraph(f"OBSERVACIONES", estilo_titulos_tabla)],
            ['', Paragraph(f"Estudiantes No Expirados Nivel BASICO", estilo_cuerpo_tabla), '', Paragraph(f"{cantidad_estudiantes_no_expirados_basico}", estilo_cantidad_tabla), Paragraph(f"", estilo_cuerpo_tabla)],
            ['', Paragraph(f"Estudiantes No Expirados Nivel INTERMEDIO", estilo_cuerpo_tabla), '', Paragraph(f"{cantidad_estudiantes_no_expirados_intermedio}", estilo_cantidad_tabla), Paragraph(f"", estilo_cuerpo_tabla)],
            ['', Paragraph(f"Estudiantes No Expirados Nivel AVANZADO", estilo_cuerpo_tabla), '', Paragraph(f"{cantidad_estudiantes_no_expirados_avanzado}", estilo_cantidad_tabla), Paragraph(f"", estilo_cuerpo_tabla)],
            ['', Paragraph(f"TOTAL ESTUDIANTES", estilo_titulos_tabla), '', Paragraph(f"{total_no_expirados}", estilo_titulos_tabla), ''],
            [Paragraph(f"Son {total_no_expirados} estudiantes que realizan sus reservas y se toman en cuenta como activos", estilo_cantidad_tabla), '', '', '', '']
        ], colWidths=ancho_columnas)

        tabla_no_expirados.setStyle(estilo_tabla_datos_est)

        elementos.append(tabla_no_expirados)
        elementos.append(Spacer(1, 20))




        tabla_expirados = Table([
            ['', Paragraph(f"DETALLE ESTUDIANTES EXPIRADOS", estilo_titulos_tabla), '', Paragraph(f"NÚMERO DE ESTUDIANTES", estilo_titulos_tabla), Paragraph(f"OBSERVACIONES", estilo_titulos_tabla)],
            ['', Paragraph(f"Estudiantes Expirados Nivel BASICO", estilo_cuerpo_tabla), '', Paragraph(f"{cantidad_estudiantes_expirados_basico}", estilo_cantidad_tabla), Paragraph(f"", estilo_cuerpo_tabla)],
            ['', Paragraph(f"Estudiantes Expirados Nivel INTERMEDIO", estilo_cuerpo_tabla), '', Paragraph(f"{cantidad_estudiantes_expirados_intermedio}", estilo_cantidad_tabla), Paragraph(f"", estilo_cuerpo_tabla)],
            ['', Paragraph(f"Estudiantes Expirados Nivel AVANZADO", estilo_cuerpo_tabla), '', Paragraph(f"{cantidad_estudiantes_expirados_avanzado}", estilo_cantidad_tabla), Paragraph(f"", estilo_cuerpo_tabla)],
            ['', Paragraph(f"TOTAL ESTUDIANTES", estilo_titulos_tabla), '', Paragraph(f"{total_expirados}", estilo_titulos_tabla), ''],
            [Paragraph(f"Son {total_expirados} estudiantes que tienen contrato expirado", estilo_cantidad_tabla), '', '', '', '']
        ], colWidths=ancho_columnas)

        tabla_expirados.setStyle(estilo_tabla_datos_est)

        elementos.append(tabla_expirados)
        elementos.append(Spacer(1, 20))



        tabla_nuevos = Table([
            ['', Paragraph(f"DETALLE ESTUDIANTES WELCOME", estilo_titulos_tabla), '', Paragraph(f"NÚMERO DE ESTUDIANTES", estilo_titulos_tabla), Paragraph(f"OBSERVACIONES", estilo_titulos_tabla)],
            ['', Paragraph(f"WELCOME", estilo_cuerpo_tabla), '', Paragraph(f"{cantidad_estudiantes_nuevos}", estilo_cantidad_tabla), Paragraph(f"", estilo_cuerpo_tabla)],
            [Paragraph(f"Estudiantes Nuevos", estilo_cantidad_tabla), '', '', '', '']
        ], colWidths=ancho_columnas)

        tabla_nuevos.setStyle(estilo_tabla_datos_wel)

        elementos.append(tabla_nuevos)
        elementos.append(Spacer(1, 20))




        tabla_concluidos = Table([
            ['', Paragraph(f"DETALLES DE ESTUDIANTES QUE CONCLUYERON EL PROGRAMA", estilo_titulos_tabla), '', Paragraph(f"NÚMERO DE ESTUDIANTES", estilo_titulos_tabla), Paragraph(f"OBSERVACIONES", estilo_titulos_tabla)],
            ['', Paragraph(f"Estudiantes que terminaron", estilo_cuerpo_tabla), '', Paragraph(f"{cantidad_estudiantes_concluidos}", estilo_cantidad_tabla), Paragraph(f"", estilo_cuerpo_tabla)]
        ], colWidths=ancho_columnas)

        tabla_concluidos.setStyle(estilo_tabla_datos_concluido)

        elementos.append(tabla_concluidos)
        elementos.append(Spacer(1, 20))








        tabla_depurados = Table([
            ['', Paragraph(f"DETALLE ESTUDIANTES DEPURADOS", estilo_titulos_tabla), '', Paragraph(f"NÚMERO DE ESTUDIANTES", estilo_titulos_tabla), Paragraph(f"OBSERVACIONES", estilo_titulos_tabla)],
            ['', Paragraph(f"Estudiantes Depurados Nivel BASICO", estilo_cuerpo_tabla), '', Paragraph(f"{cantidad_estudiantes_depurados_basico}", estilo_cantidad_tabla), Paragraph(f"", estilo_cuerpo_tabla)],
            ['', Paragraph(f"Estudiantes Depurados Nivel INTERMEDIO", estilo_cuerpo_tabla), '', Paragraph(f"{cantidad_estudiantes_depurados_intermedio}", estilo_cantidad_tabla), Paragraph(f"", estilo_cuerpo_tabla)],
            ['', Paragraph(f"Estudiantes Depurados Nivel AVANZADO", estilo_cuerpo_tabla), '', Paragraph(f"{cantidad_estudiantes_depurados_avanzado}", estilo_cantidad_tabla), Paragraph(f"", estilo_cuerpo_tabla)],
            ['', Paragraph(f"TOTAL ESTUDIANTES", estilo_titulos_tabla), '', Paragraph(f"{total_depurados}", estilo_titulos_tabla), ''],
            [Paragraph(f"Son {total_depurados} estudiantes que tienen su contrato expirado del mes de {mes_depurado_uno}, {mes_depurado_dos} y {mes_depurado_tres} con los cuales se comunico en su momento.", estilo_cantidad_tabla), '', '', '', '']
        ], colWidths=ancho_columnas)

        tabla_depurados.setStyle(estilo_tabla_datos_est)

        elementos.append(tabla_depurados)
        elementos.append(Spacer(1, 3*inch))

        estilo_firma = ParagraphStyle('titulo_tabla', fontSize=12, alignment=1, fontName="Helvetica-Bold", textColor=colors.black)

        elementos.append(Paragraph("__________________________________", estilo_firma))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph("RECEPCIÓN", estilo_firma))

        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer
    

    # ------------------------------- informes -----------------------------
    def generar_informe_carga_horaria_docentes_mes_pdf(nombre_usuario, fecha):

        
        


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
        #logo_direccion = os.path.join('var', 'www', 'OkAprendeIngles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 0.8 * inch, 0.8 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ano_actual = datetime.now().strftime("%Y")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo_2)


        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.2 * inch), height - (0.2 * inch) - imagen_logo.drawHeight)

            titulo_x = width / 2  
            titulo_y = height - (0.5 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x + 130, titulo_y, f"NOTA INTERNA")

            titulo_x = width / 2  
            titulo_y = height - (0.7 * inch) 
            canvas.setFont("Helvetica-Bold", 11)
            canvas.drawString(titulo_x + 210, titulo_y, f"D.T. /{ano_actual}")

            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        #elementos.append(Spacer(1, 20))

        fecha_objetivo = datetime.strptime(fecha, "%Y-%m-%d")

        mes_actual = fecha_objetivo.date()
        mes_actual = mes_actual.replace(day=1)

        fecha_no_expirados = fecha_objetivo + relativedelta(months=1)
        fecha_no_expirados = fecha_no_expirados.date()
        fecha_no_expirados = fecha_no_expirados.replace(day=1)

        
        fecha_actual = datetime.now()

        
        
        fecha_actual_str = fecha_actual.strftime("%d/%m/%Y")
        mes_string = MES_INGLES[mes_actual.strftime("%B")]
        fecha_mes_str = mes_actual.strftime("%d/%m/%Y")
        ultimo_dia = fecha_no_expirados - timedelta(days=1)
        ultimo_dia_str = ultimo_dia.strftime("%d/%m/%Y")

        estilo_inicio = ParagraphStyle('Inicio', fontSize=8, alignment=0) 
        estilo_cuerpo = ParagraphStyle('Cuerpo', fontSize=8, alignment=1)

        ancho_columnas = [0.5*inch, 1*inch, 3*inch, 1*inch, 1*inch]

        tabla_datos = Table([
            [Paragraph(f"<b>PARA:</b>", estilo_inicio), '', Paragraph(f"<b>SR(A). CARLA VACAFLORES</b>", estilo_inicio), '', ''],
            ['', '', Paragraph(f"<b>DIRECTORA GENERAL</b>", estilo_inicio), '', ''],
            [Paragraph(f"<b>DE:</b>", estilo_inicio), '', Paragraph(f"<b>RECEPCIÓN</b>", estilo_inicio), '', ''],
            ['', '', '', '', ''],
            [Paragraph(f"<b>ASUNTO:</b>", estilo_inicio), '', Paragraph(f"<b>ENTREGA INFORME MENSUAL {mes_string}</b>", estilo_inicio), '', ''],
            [Paragraph(f"<b>FECHA:</b>", estilo_inicio), '', Paragraph(f"<b>{fecha_actual_str}</b>", estilo_inicio), '', ''],
            [Paragraph(f"Cordial saludo:", estilo_inicio), '', '', '', ''],
            [Paragraph(f"INFORME CARGA HORARIA MENSUAL DEL {fecha_mes_str} al {ultimo_dia_str}", estilo_cuerpo), '', Paragraph(f" Mediante la presente me dirijo a su persona para hacerle entrega de informe mensual correspondiente al mes de {mes_string} de {ano_actual} del Departamento Tutorial, el mismo que se detalla a continuación:", estilo_cuerpo), '', '']
        ], colWidths=ancho_columnas)

        estilo_tabla = TableStyle([
                                ('SPAN', (0, 0), (1, 0)),
                                ('SPAN', (2, 0), (-1, 0)),
                                ('SPAN', (0, 1), (1, 1)),
                                ('SPAN', (2, 1), (-1, 1)),
                                ('SPAN', (0, 2), (1, 2)),
                                ('SPAN', (2, 2), (-1, 2)),
                                ('SPAN', (0, 4), (1, 4)),
                                ('SPAN', (2, 4), (-1, 4)),
                                ('SPAN', (0, 5), (1, 5)),
                                ('SPAN', (2, 5), (-1, 5)),
                                ('SPAN', (0, 6), (1, 6)),
                                ('SPAN', (2, 6), (-1, 6)),
                                ('SPAN', (0, 7), (1, 7)),
                                ('SPAN', (2, 7), (-1, 7)),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
        
        tabla_datos.setStyle(estilo_tabla)

        elementos.append(tabla_datos)
        elementos.append(Spacer(1, 20))

        color_titulos_tabla = hex_to_color('#4472C4')

        estilo_tabla_datos_est = TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), color_titulos_tabla),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
        
        estilo_tabla_datos_wel = TableStyle([
                                ('SPAN', (1, 0), (2, 0)),
                                ('SPAN', (1, 1), (2, 1)),
                                ('SPAN', (0, 2), (-1, 2)),
                                ('BACKGROUND', (0, 0), (-1, 0), color_titulos_tabla),
                                ('BACKGROUND', (0, 2), (-1, 2), colors.yellow),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
        
        estilo_tabla_datos_concluido = TableStyle([
                                ('SPAN', (1, 0), (2, 0)),
                                ('SPAN', (1, 1), (2, 1)),
                                ('BACKGROUND', (0, 0), (-1, 0), color_titulos_tabla),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])

        estilo_titulos_tabla = ParagraphStyle('titulo_tabla', fontSize=8, alignment=1, fontName="Helvetica-Bold", textColor=colors.white)
        estilo_cuerpo_tabla = ParagraphStyle('cuerpo_tabla', fontSize=8, alignment=1, fontName="Helvetica-Bold", textColor=colors.black)
        estilo_cantidad_tabla = ParagraphStyle('cantidad_tabla', fontSize=8, alignment=1, textColor=colors.black)
        estilo_titulo_nombre = ParagraphStyle('titulo_tabla', fontSize=12, alignment=0, fontName="Helvetica-Bold", textColor=colors.black)


        docentes = Docente.query.filter(Docente.activo==1).all()

        ancho_columnas_carga = [2*inch, 0.8*inch, 2*inch, 0.8*inch, 1.4*inch]
        ancho_columnas_total = 0
        contador_tablas = 0
        for ancho in ancho_columnas_carga:
            ancho_columnas_total = ancho_columnas_total + ancho
        for docente in docentes:
            horarios = "llenar horarios para calcular tiempos"
            nombres_docente = str(docente.nombres).upper() + " " + str(docente.apellidos).upper()
            #detalles_sesiones = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, DetalleSesion.id_sesion==Sesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.fecha>=mes_actual, Sesion.fecha<fecha_no_expirados).all()
            #sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.fecha>=mes_actual, Sesion.fecha<fecha_no_expirados).all()
            fecha_aux = mes_actual
            if fecha_aux.strftime("%A")=='Sunday':
                fecha_aux = fecha_aux + timedelta(days=1)

            inicio_semana = fecha_aux.strftime("%d-%m-%Y")
            fin_semana = fecha_aux.strftime("%d-%m-%Y")

            cantidad_asistidas = 0
            contador_semana = 1

            datos_tabla = []

            while fecha_aux<fecha_no_expirados:

                if fecha_aux.strftime("%A")=='Sunday':

                    fila_tabla = [[inicio_semana, fin_semana], cantidad_asistidas, contador_semana]
                    contador_semana = contador_semana + 1
                    cantidad_asistidas = 0
                    datos_tabla.append(fila_tabla)


                    fecha_aux = fecha_aux + timedelta(days=1)
                    inicio_semana = fecha_aux.strftime("%d-%m-%Y")
                    fin_semana = fecha_aux.strftime("%d-%m-%Y")
                    continue


                sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.fecha==fecha_aux, Sesion.id_docente==docente.id_docente).all()
                if sesiones:
                    for sesion in sesiones:
                        id_sesion_obj = sesion.id_sesion
                        cantidad_asist = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion_obj, DetalleSesion.estado_registro=='Asistio').count()
                        if cantidad_asist>0:
                            cantidad_asistidas = cantidad_asistidas + 1
                fin_semana = fecha_aux.strftime("%d-%m-%Y")
                fecha_aux = fecha_aux + timedelta(days=1)
            

            fila_tabla = [[inicio_semana, fin_semana], cantidad_asistidas, contador_semana]
            datos_tabla.append(fila_tabla)


            tabla_docente = []
            cabecera = [Paragraph(f"SEMANA", estilo_titulos_tabla), Paragraph(f"CARGA HORARIA", estilo_titulos_tabla), Paragraph(f"TURNO", estilo_titulos_tabla), Paragraph(f"M/T - T/C", estilo_titulos_tabla), Paragraph(f"OBSERVACIONES", estilo_titulos_tabla)]
            
            tabla_docente.append(cabecera)

            horas_totales = 0

            for dato_t in datos_tabla:
                inicio_s = dato_t[0][0]
                fin_s = dato_t[0][1]
                horas_totales = horas_totales + dato_t[1]

                #semanas = Paragraph(f"{inicio_s}", estilo_cantidad_tabla)
                dato_string = ""

                if inicio_s != fin_s:
                    dia_ini = inicio_s.split('-')[0]
                    dia_fin = fin_s.split('-')[0]
                    dato_string = f"Del {dia_ini} al {dia_fin} de {mes_string} {ano_actual}"
                else:
                    dia_ini = inicio_s.split('-')[0]
                    dato_string = f"{dia_ini} de {mes_string} de {ano_actual}"
                fila_pd = [Paragraph(f"{dato_string}", estilo_cantidad_tabla), Paragraph(f"{dato_t[1]} hrs", estilo_cantidad_tabla), Paragraph(f"Mañana Tarde Noche", estilo_cantidad_tabla), Paragraph(f"M/T - T/C", estilo_cantidad_tabla), Paragraph(f"Semana {dato_t[2]}", estilo_cantidad_tabla)]
                tabla_docente.append(fila_pd)
            
            final = [Paragraph(f"TOTAL HORAS TRABAJADAS", estilo_cuerpo_tabla), Paragraph(f"{horas_totales} hrs", estilo_cuerpo_tabla), '', '', '']
                
            tabla_docente.append(final)

            tabla_docente_pdf = Table(tabla_docente, colWidths=ancho_columnas_carga)
            tabla_docente_pdf.setStyle(estilo_tabla_datos_est)

            tabla_nombre = Table([[Paragraph(f"{nombres_docente}", estilo_titulo_nombre)]], colWidths=ancho_columnas_total)

            elementos.append(tabla_nombre)
            elementos.append(Spacer(1, 10))
            elementos.append(tabla_docente_pdf)
            elementos.append(Spacer(1, 20))

            contador_tablas = contador_tablas + 1
            if contador_tablas == 2:
                elementos.append(PageBreak())
            elif (contador_tablas-5>0 and contador_tablas%3==2):
                elementos.append(PageBreak())


        elementos.append(Spacer(1, 3*inch))
        estilo_firma = ParagraphStyle('titulo_tabla', fontSize=12, alignment=1, fontName="Helvetica-Bold", textColor=colors.black)

        elementos.append(Paragraph("__________________________________", estilo_firma))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph("RECEPCIÓN", estilo_firma))

        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer



    def generar_informe_carga_horaria_docentes_semana_pdf(nombre_usuario, fecha):

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
        #logo_direccion = os.path.join('var', 'www', 'OkAprendeIngles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 0.8 * inch, 0.8 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ano_actual = datetime.now().strftime("%Y")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo_2)


        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.2 * inch), height - (0.2 * inch) - imagen_logo.drawHeight)

            titulo_x = width / 2  
            titulo_y = height - (0.5 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x + 130, titulo_y, f"NOTA INTERNA")

            titulo_x = width / 2  
            titulo_y = height - (0.7 * inch) 
            canvas.setFont("Helvetica-Bold", 11)
            canvas.drawString(titulo_x + 210, titulo_y, f"D.T. /{ano_actual}")

            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        #elementos.append(Spacer(1, 20))

        fecha_objetivo = datetime.strptime(fecha, "%Y-%m-%d")

        mes_actual = fecha_objetivo.date()
        dias_al_lunes = mes_actual.weekday()
        mes_actual = mes_actual - timedelta(days=dias_al_lunes)
        #mes_actual = mes_actual.replace(day=1)

        fecha_no_expirados = mes_actual + timedelta(days=6)

        #fecha_no_expirados = fecha_no_expirados.replace(day=1)

        
        fecha_actual = datetime.now()

        
        
        fecha_actual_str = fecha_actual.strftime("%d/%m/%Y")
        mes_string = MES_INGLES[mes_actual.strftime("%B")]
        fecha_mes_str = mes_actual.strftime("%d/%m/%Y")
        ultimo_dia = fecha_no_expirados - timedelta(days=1)
        ultimo_dia_str = ultimo_dia.strftime("%d/%m/%Y")

        estilo_inicio = ParagraphStyle('Inicio', fontSize=8, alignment=0) 
        estilo_cuerpo = ParagraphStyle('Cuerpo', fontSize=8, alignment=1)

        ancho_columnas = [0.5*inch, 1*inch, 3*inch, 1*inch, 1*inch]

        tabla_datos = Table([
            [Paragraph(f"<b>PARA:</b>", estilo_inicio), '', Paragraph(f"<b>SR(A). CARLA VACAFLORES</b>", estilo_inicio), '', ''],
            ['', '', Paragraph(f"<b>DIRECTORA GENERAL</b>", estilo_inicio), '', ''],
            [Paragraph(f"<b>DE:</b>", estilo_inicio), '', Paragraph(f"<b>RECEPCIÓN</b>", estilo_inicio), '', ''],
            ['', '', '', '', ''],
            [Paragraph(f"<b>ASUNTO:</b>", estilo_inicio), '', Paragraph(f"<b>ENTREGA INFORME SEMANAL</b>", estilo_inicio), '', ''],
            [Paragraph(f"<b>FECHA:</b>", estilo_inicio), '', Paragraph(f"<b>{fecha_actual_str}</b>", estilo_inicio), '', ''],
            [Paragraph(f"Cordial saludo:", estilo_inicio), '', '', '', ''],
            [Paragraph(f"INFORME CARGA HORARIA SEMANAL DEL {fecha_mes_str} al {ultimo_dia_str}", estilo_cuerpo), '', Paragraph(f" Mediante la presente me dirijo a su persona para hacerle entrega de informe semanal del Departamento Tutorial, el mismo que se detalla a continuación:", estilo_cuerpo), '', '']
        ], colWidths=ancho_columnas)

        estilo_tabla = TableStyle([
                                ('SPAN', (0, 0), (1, 0)),
                                ('SPAN', (2, 0), (-1, 0)),
                                ('SPAN', (0, 1), (1, 1)),
                                ('SPAN', (2, 1), (-1, 1)),
                                ('SPAN', (0, 2), (1, 2)),
                                ('SPAN', (2, 2), (-1, 2)),
                                ('SPAN', (0, 4), (1, 4)),
                                ('SPAN', (2, 4), (-1, 4)),
                                ('SPAN', (0, 5), (1, 5)),
                                ('SPAN', (2, 5), (-1, 5)),
                                ('SPAN', (0, 6), (1, 6)),
                                ('SPAN', (2, 6), (-1, 6)),
                                ('SPAN', (0, 7), (1, 7)),
                                ('SPAN', (2, 7), (-1, 7)),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
        
        tabla_datos.setStyle(estilo_tabla)

        elementos.append(tabla_datos)
        elementos.append(Spacer(1, 20))

        color_titulos_tabla = hex_to_color('#4472C4')

        estilo_tabla_datos_est = TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), color_titulos_tabla),
                                ('SPAN', (0, -1), (1, -1)),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
        
        estilo_tabla_datos_wel = TableStyle([
                                ('SPAN', (1, 0), (2, 0)),
                                ('SPAN', (1, 1), (2, 1)),
                                ('SPAN', (0, 2), (-1, 2)),
                                ('BACKGROUND', (0, 0), (-1, 0), color_titulos_tabla),
                                ('BACKGROUND', (0, 2), (-1, 2), colors.yellow),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
        
        estilo_tabla_datos_concluido = TableStyle([
                                ('SPAN', (1, 0), (2, 0)),
                                ('SPAN', (1, 1), (2, 1)),
                                ('BACKGROUND', (0, 0), (-1, 0), color_titulos_tabla),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])

        estilo_titulos_tabla = ParagraphStyle('titulo_tabla', fontSize=8, alignment=1, fontName="Helvetica-Bold", textColor=colors.white)
        estilo_cuerpo_tabla = ParagraphStyle('cuerpo_tabla', fontSize=8, alignment=1, fontName="Helvetica-Bold", textColor=colors.black)
        estilo_cantidad_tabla = ParagraphStyle('cantidad_tabla', fontSize=8, alignment=1, textColor=colors.black)
        estilo_titulo_nombre = ParagraphStyle('titulo_tabla', fontSize=12, alignment=0, fontName="Helvetica-Bold", textColor=colors.black)


        docentes = Docente.query.filter(Docente.activo==1).all()

        ancho_columnas_carga = [0.7*inch, 1.4*inch, 0.7*inch, 1.3*inch, 0.7*inch, 2*inch]
        ancho_columnas_total = 0
        contador_tablas = 0
        for ancho in ancho_columnas_carga:
            ancho_columnas_total = ancho_columnas_total + ancho
        for docente in docentes:
            horarios = "llenar horarios para calcular tiempos"
            nombres_docente = str(docente.nombres).upper() + " " + str(docente.apellidos).upper()
            #detalles_sesiones = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, DetalleSesion.id_sesion==Sesion.id_sesion).filter(DetalleSesion.activo==1, Sesion.fecha>=mes_actual, Sesion.fecha<fecha_no_expirados).all()
            #sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.fecha>=mes_actual, Sesion.fecha<fecha_no_expirados).all()
            fecha_aux = mes_actual
            if fecha_aux.strftime("%A")=='Sunday':
                fecha_aux = fecha_aux + timedelta(days=1)

            inicio_semana = fecha_aux.strftime("%d-%m-%Y")
            fin_semana = fecha_aux.strftime("%d-%m-%Y")

            cantidad_asistidas = 0
            contador_semana = 1

            datos_tabla = []

            while fecha_aux<fecha_no_expirados:

                '''if fecha_aux.strftime("%A")=='Sunday':

                    fila_tabla = [[inicio_semana, fin_semana], cantidad_asistidas, contador_semana]
                    contador_semana = contador_semana + 1
                    cantidad_asistidas = 0
                    datos_tabla.append(fila_tabla)


                    fecha_aux = fecha_aux + timedelta(days=1)
                    inicio_semana = fecha_aux.strftime("%d-%m-%Y")
                    fin_semana = fecha_aux.strftime("%d-%m-%Y")
                    continue'''


                sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.fecha==fecha_aux, Sesion.id_docente==docente.id_docente).all()
                if sesiones:
                    for sesion in sesiones:
                        id_sesion_obj = sesion.id_sesion
                        cantidad_asist = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion_obj, DetalleSesion.estado_registro=='Asistio').count()
                        if cantidad_asist>0:
                            cantidad_asistidas = cantidad_asistidas + 1
                fin_semana = fecha_aux.strftime("%d-%m-%Y")
                fecha_aux = fecha_aux + timedelta(days=1)
                fila_tabla = [fin_semana, cantidad_asistidas]
                contador_semana = contador_semana + 1
                cantidad_asistidas = 0
                datos_tabla.append(fila_tabla)

            

            #fila_tabla = [[inicio_semana, fin_semana], cantidad_asistidas, contador_semana]
            #datos_tabla.append(fila_tabla)


            tabla_docente = []
            cabecera = [Paragraph(f"DIA", estilo_titulos_tabla), Paragraph(f"FECHA", estilo_titulos_tabla), Paragraph(f"CARGA HORARIA", estilo_titulos_tabla), Paragraph(f"TURNO", estilo_titulos_tabla), Paragraph(f"M/T - T/C", estilo_titulos_tabla), Paragraph(f"OBSERVACIONES", estilo_titulos_tabla)]
            
            tabla_docente.append(cabecera)

            horas_totales = 0

            for dato_t in datos_tabla:
                inicio_s = dato_t[0]
                horas_totales = horas_totales + dato_t[1]

                #semanas = Paragraph(f"{inicio_s}", estilo_cantidad_tabla)
                
                dia_ini = inicio_s.split('-')[0]
                dato_string = f"{dia_ini} de {mes_string} de {ano_actual}"

                fecha_objt = datetime.strptime(inicio_s, "%d-%m-%Y")


                dia_string = DIAS_INGLES[fecha_objt.strftime("%A")]

                
                fila_pd = [Paragraph(f"{dia_string}", estilo_cantidad_tabla), Paragraph(f"{dato_string}", estilo_cantidad_tabla), Paragraph(f"{dato_t[1]} hrs", estilo_cantidad_tabla), Paragraph(f"Mañana Tarde Noche", estilo_cantidad_tabla), Paragraph(f"M/T - T/C", estilo_cantidad_tabla), Paragraph(f"", estilo_cantidad_tabla)]
                tabla_docente.append(fila_pd)
            
            final = [Paragraph(f"TOTAL HORAS TRABAJADAS", estilo_cuerpo_tabla), '', Paragraph(f"{horas_totales} hrs", estilo_cuerpo_tabla), '', '', '']
                
            tabla_docente.append(final)

            tabla_docente_pdf = Table(tabla_docente, colWidths=ancho_columnas_carga)
            tabla_docente_pdf.setStyle(estilo_tabla_datos_est)

            tabla_nombre = Table([[Paragraph(f"{nombres_docente}", estilo_titulo_nombre)]], colWidths=ancho_columnas_total)

            elementos.append(tabla_nombre)
            elementos.append(Spacer(1, 10))
            elementos.append(tabla_docente_pdf)
            elementos.append(Spacer(1, 20))

            contador_tablas = contador_tablas + 1
            if contador_tablas == 2:
                elementos.append(PageBreak())
            elif (contador_tablas-5>0 and contador_tablas%3==2):
                elementos.append(PageBreak())


        elementos.append(Spacer(1, 3*inch))
        estilo_firma = ParagraphStyle('titulo_tabla', fontSize=12, alignment=1, fontName="Helvetica-Bold", textColor=colors.black)

        elementos.append(Paragraph("__________________________________", estilo_firma))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph("RECEPCIÓN", estilo_firma))

        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer
    
    def generar_informe_carga_horaria_docentes_semana_detallado_pdf(nombre_usuario, fecha):

        margin_left = 0.6 * inch
        margin_right = 0.6 * inch
        margin_top = 1.2 * inch  # Deja espacio para el carimbo
        margin_bottom = 1 * inch

        rojo_fuerte = colors.Color(1, 0.298, 0.298)      # #FF4C4C
        naranja_suave = colors.Color(1, 0.835, 0.502)    # #FFD580
        amarillo_claro = colors.Color(1, 1, 0.6)         # #FFFF99
        verde_claro = colors.Color(0.698, 0.949, 0.698)  # #B2F2B2

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter), 
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
        #logo_direccion = os.path.join('var', 'www', 'OkAprendeIngles', 'app', 'static', 'img', 'logo.jpeg')
        imagen_logo = Image(logo_direccion, 0.8 * inch, 0.8 * inch)  

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ano_actual = datetime.now().strftime("%Y")
        generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}<br/><b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo_2)


        def add_header(canvas, doc):
            width, height = letter
            imagen_logo.drawOn(canvas, (0.2 * inch), width - (0.2 * inch) - imagen_logo.drawHeight)

            titulo_x = height / 2  
            titulo_y = width - (0.5 * inch) 
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(titulo_x, titulo_y, f"WEEKLY STATICTICS CONTROL")

            titulo_x = height / 2  
            titulo_y = width - (0.7 * inch) 
            canvas.setFont("Helvetica-Bold", 11)
            canvas.drawString(titulo_x, titulo_y, f"TUTORIAL DEPARTAMENT")

            posicion_texto_x = (0.3*inch)
            posicion_texto_y = (0.3*inch)
            generado_por.wrapOn(canvas, width, height)
            generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)

        
        #elementos.append(Spacer(1, 20))

        fecha_objetivo = datetime.strptime(fecha, "%Y-%m-%d")

        mes_actual = fecha_objetivo.date()
        dias_al_lunes = mes_actual.weekday()
        mes_actual = mes_actual - timedelta(days=dias_al_lunes)
        #mes_actual = mes_actual.replace(day=1)

        fecha_no_expirados = mes_actual + timedelta(days=6)

        #fecha_no_expirados = fecha_no_expirados.replace(day=1)

        
        fecha_actual = datetime.now()

        
        
        fecha_actual_str = fecha_actual.strftime("%d/%m/%Y")
        mes_string = MES_INGLES[mes_actual.strftime("%B")]
        fecha_mes_str = mes_actual.strftime("%d/%m/%Y")
        ultimo_dia = fecha_no_expirados - timedelta(days=1)
        ultimo_dia_str = ultimo_dia.strftime("%d/%m/%Y")

        estilo_inicio = ParagraphStyle('Inicio', fontSize=8, alignment=0) 
        estilo_cuerpo = ParagraphStyle('Cuerpo', fontSize=8, alignment=1)


        estilo_tabla = TableStyle([
                                ('SPAN', (0, 0), (1, 0)),
                                ('SPAN', (2, 0), (-1, 0)),
                                ('SPAN', (0, 1), (1, 1)),
                                ('SPAN', (2, 1), (-1, 1)),
                                ('SPAN', (0, 2), (1, 2)),
                                ('SPAN', (2, 2), (-1, 2)),
                                ('SPAN', (0, 4), (1, 4)),
                                ('SPAN', (2, 4), (-1, 4)),
                                ('SPAN', (0, 5), (1, 5)),
                                ('SPAN', (2, 5), (-1, 5)),
                                ('SPAN', (0, 6), (1, 6)),
                                ('SPAN', (2, 6), (-1, 6)),
                                ('SPAN', (0, 7), (1, 7)),
                                ('SPAN', (2, 7), (-1, 7)),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
        

        color_titulos_tabla = hex_to_color('#4472C4')
        color_titulos_tabla = colors.skyblue
        

        estilo_tabla_datos_est = [
                                ('BACKGROUND', (0, 0), (0, 0), colors.blue),
                                ('BACKGROUND', (1, 0), (3, 0), colors.red),
                                ('BACKGROUND', (4, 0), (6, 0), colors.blue),
                                ('BACKGROUND', (7, 0), (9, 0), colors.red),
                                ('BACKGROUND', (10, 0), (12, 0), colors.blue),
                                ('BACKGROUND', (13, 0), (15, 0), colors.red),
                                ('BACKGROUND', (16, 0), (18, 0), colors.blue),
                                ('BACKGROUND', (19, 0), (19, 0), colors.red),
                                ('SPAN', (2, 0), (3, 0)),
                                ('SPAN', (5, 0), (6, 0)),
                                ('SPAN', (8, 0), (9, 0)),
                                ('SPAN', (11, 0), (12, 0)),
                                ('SPAN', (14, 0), (15, 0)),
                                ('SPAN', (17, 0), (18, 0)),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]
        

        #estilo_tabla_datos_est = TableStyle()
        
        estilo_tabla_datos_wel = TableStyle([
                                ('SPAN', (1, 0), (2, 0)),
                                ('SPAN', (1, 1), (2, 1)),
                                ('SPAN', (0, 2), (-1, 2)),
                                ('BACKGROUND', (0, 0), (-1, 0), color_titulos_tabla),
                                ('BACKGROUND', (0, 2), (-1, 2), colors.yellow),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
        
        estilo_tabla_datos_concluido = TableStyle([
                                ('SPAN', (1, 0), (2, 0)),
                                ('SPAN', (1, 1), (2, 1)),
                                ('BACKGROUND', (0, 0), (-1, 0), color_titulos_tabla),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])

        estilo_titulos_tabla = ParagraphStyle('titulo_tabla', fontSize=6, alignment=1, fontName="Helvetica-Bold", textColor=colors.white)
        estilo_cuerpo_tabla = ParagraphStyle('cuerpo_tabla', fontSize=8, alignment=1, fontName="Helvetica-Bold", textColor=colors.black)
        estilo_cantidad_tabla = ParagraphStyle('cantidad_tabla', fontSize=6, alignment=1, textColor=colors.black)
        estilo_titulo_nombre = ParagraphStyle('titulo_tabla', fontSize=12, alignment=0, fontName="Helvetica-Bold", textColor=colors.black)

        lista_horas = ['07:30', '08:30', '09:30', '10:30', '11:30', '12:30', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00']

        docentes = Docente.query.filter(Docente.activo==1).all()

        ancho_columnas_carga = [0.7*inch, 1.4*inch, 0.7*inch, 1.3*inch, 0.7*inch, 2*inch]


        flag_color = True

        contador_celdas = 0
        contador_celdas_tutor = 1
        
        tabla_general = []

        fecha_en_string = mes_actual.strftime("%d-%m-%Y")
        dia_en_string = fecha_en_string.split('-')[0]

        dia_numero = int(dia_en_string)
        fecha_lunes_s = mes_actual.day
        fecha_martes_s = (mes_actual + timedelta(days=1)).day
        fecha_miercoles_s = (mes_actual + timedelta(days=2)).day
        fecha_jueves_s = (mes_actual + timedelta(days=3)).day
        fecha_viernes_s = (mes_actual + timedelta(days=4)).day
        fecha_sabado_s = (mes_actual + timedelta(days=5)).day


        cabecera = [Paragraph(f"TUTOR", estilo_titulos_tabla), Paragraph(f"HORA", estilo_titulos_tabla), Paragraph(f"LUNES {fecha_lunes_s}", estilo_titulos_tabla), '', Paragraph(f"HORA", estilo_titulos_tabla), Paragraph(f"MARTES {fecha_martes_s}", estilo_titulos_tabla), '', Paragraph(f"HORA", estilo_titulos_tabla), Paragraph(f"MIERCOLES {fecha_miercoles_s}", estilo_titulos_tabla), '', Paragraph(f"HORA", estilo_titulos_tabla), Paragraph(f"JUEVES {fecha_jueves_s}", estilo_titulos_tabla), '', Paragraph(f"HORA", estilo_titulos_tabla), Paragraph(f"VIERNES {fecha_viernes_s}", estilo_titulos_tabla), '', Paragraph(f"HORA", estilo_titulos_tabla), Paragraph(f"SABADO {fecha_sabado_s}", estilo_titulos_tabla), '', Paragraph(f"TOTAL", estilo_titulos_tabla)]

        tabla_general.append(cabecera)

        datos_docente_general = []

        if docentes:

            for docente in docentes:
                #flag_color = not flag_color
                contador_celdas_tutor = 0

                fecha_aux = mes_actual

                nombres_doc = str(docente.nombres).split(' ')[0] + " " + str(docente.apellidos).split(' ')[0]

                id_docente_obj = docente.id_docente

                diccionario_horas = {}

                lista_dias = []

                cantida_tot = 0
                

                while fecha_aux<fecha_no_expirados:
                    diccionario_datos = {}
                    sesiones = Sesion.query.filter(Sesion.activo==1, Sesion.id_docente==id_docente_obj, Sesion.fecha==fecha_aux).order_by(Sesion.fecha, Sesion.hora).all()
                    if sesiones:
                        for sesion in sesiones:
                            id_sesion_obj = sesion.id_sesion
                            hora_sesion = sesion.hora.strftime("%H:%M")
                            diccionario_horas[hora_sesion] = True
                            if (str(sesion.nivel)=='0'):
                                seccion_nivel = str(sesion.seccion)
                            else:
                                seccion_nivel = str(sesion.seccion) + " " + str(sesion.nivel)
                            cantidad_asistentes = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion_obj, DetalleSesion.estado_registro=='Asistio').count()
                            cantidad_reservados = DetalleSesion.query.filter(DetalleSesion.activo==1, DetalleSesion.id_sesion==id_sesion_obj).count()
                            if cantidad_asistentes > 0:
                                cantida_tot = cantida_tot + 1
                            #cantida_tot = cantida_tot + int(cantidad_asistentes)
                            dato_registros = str(cantidad_asistentes) + "/" + str(cantidad_reservados)

                            diccionario_datos[hora_sesion] = [seccion_nivel, dato_registros]
                    
                    lista_dias.append(diccionario_datos)
                    fecha_aux = fecha_aux + timedelta(days=1)
                datos_docente_general.append([diccionario_horas, lista_dias, nombres_doc, cantida_tot])
        

        lista_spans = []
        if len(datos_docente_general)>0:
            for dato_docente in datos_docente_general:
                
                dict_horas = dato_docente[0]
                if len(dict_horas)>0:
                    flag_color = not flag_color
                    list_dias = dato_docente[1]
                    nombre_doc = dato_docente[2]
                    totales = dato_docente[3]
                    inicio_span = contador_celdas + 1
                    fin_span = contador_celdas + 1
                    for hora_d in lista_horas:
                        if hora_d in dict_horas:
                            contador_celdas = contador_celdas + 1
                            fin_span = contador_celdas
                            fila_datt = []
                            fila_datt.append(Paragraph(f"{nombre_doc}", estilo_cantidad_tabla))
                            for dia_l in list_dias:
                                if hora_d in dia_l:
                                    fila_datt.append(Paragraph(f"{hora_d}", estilo_cantidad_tabla))
                                    fila_datt.append(Paragraph(f"{dia_l[hora_d][0]}", estilo_cantidad_tabla))
                                    fila_datt.append(Paragraph(f"{dia_l[hora_d][1]}", estilo_cantidad_tabla))
                                else:
                                    fila_datt.append(Paragraph(f"{hora_d}", estilo_cantidad_tabla))
                                    fila_datt.append('')
                                    fila_datt.append('')
                            
                            fila_datt.append(Paragraph(f"{totales}", estilo_cantidad_tabla))

                            tabla_general.append(fila_datt)
                                    

                    lista_spans.append([inicio_span, fin_span, flag_color])
        

        contador_spp = 1
        for spanes in lista_spans:
            coloracion_1 = ('BACKGROUND', (0, spanes[0]), (-1, spanes[1]), color_titulos_tabla)
            #coloracion_2 = ('BACKGROUND', (-1, spanes[0]), (-1, spanes[1]), color_titulos_tabla)
            #coloracion_3 = ('BACKGROUND', (1, spanes[0]), (-2, spanes[1]), color_titulos_tabla)
            if spanes[2]:
                estilo_tabla_datos_est.append(coloracion_1)
                #estilo_tabla_datos_est.append(coloracion_2)
                #estilo_tabla_datos_est.append(coloracion_3)
            span_nombre = ('SPAN', (0, spanes[0]), (0, spanes[1]))
            span_total = ('SPAN', (-1, spanes[0]), (-1, spanes[1]))
            
            estilo_tabla_datos_est.append(span_nombre)
            estilo_tabla_datos_est.append(span_total)
            
            contador_spp = contador_spp + 1
        
        estilo_tabla_datos_est = TableStyle(estilo_tabla_datos_est)
            
            
        


        tabla_general_pdf = Table(tabla_general)
        tabla_general_pdf.setStyle(estilo_tabla_datos_est)



        elementos.append(Spacer(1, 20))
        elementos.append(tabla_general_pdf)
        elementos.append(Spacer(1, 20))






        


        elementos.append(Spacer(1, 3*inch))
        estilo_firma = ParagraphStyle('titulo_tabla', fontSize=12, alignment=1, fontName="Helvetica-Bold", textColor=colors.black)

        elementos.append(Paragraph("__________________________________", estilo_firma))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph("RECEPCIÓN", estilo_firma))

        

        pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)
        buffer.seek(0)

        return buffer