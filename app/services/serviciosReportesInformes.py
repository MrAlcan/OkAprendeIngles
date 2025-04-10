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

        

        logo_direccion = os.path.join(os.getcwd(), 'app', 'static', 'img', 'logo.jpeg')
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

        detalles_sesiones = db.session.query(Sesion, DetalleSesion).join(DetalleSesion, DetalleSesion.id_sesion==Sesion.id_sesion).filter(Sesion.fecha>=mes_actual, Sesion.fecha<fecha_no_expirados, Sesion.seccion=='Test Oral', DetalleSesion.calificacion>=85, DetalleSesion.nivel_seccion==50).all()

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