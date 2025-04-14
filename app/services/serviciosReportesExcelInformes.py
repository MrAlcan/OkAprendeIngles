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
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

import os
import queue
from io import BytesIO
import xlsxwriter

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

inch = 10.71

class ServiciosReportesExcelInformes():

    def generar_informe_mensual_estudiantes_excel(nombre_usuario, fecha):

        rojo_fuerte = "#FF4C4C"
        naranja_suave =  "#FFD580"
        amarillo_claro = "#FFFF99"
        verde_claro = "#B2F2B2"

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ano_actual = datetime.now().strftime("%Y")


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



        buffer = BytesIO()

        # Crear el Workbook en memoria
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})

        # Agregar una hoja de trabajo con nombre personalizado
        worksheet = workbook.add_worksheet('Informe Estudiantes')

        # Definir formatos personalizados
        header_format = workbook.add_format({
            'bold': True, 
            'font_color': 'white', 
            'bg_color': '#4CAF50', 
            'align': 'center',
            'valign': 'vcenter'
        })
        cell_format = workbook.add_format({
            'font_color': 'blue', 
            'italic': True
        })
        # Formato para celdas unidas (merge)
        merge_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#ffffff'
        })



        # Estilos
        formato_inicio = workbook.add_format({'font_size': 8, 'align': 'left', 'valign': 'vcenter'})
        formato_cuerpo = workbook.add_format({'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
        formato_negrita = workbook.add_format({'font_size': 8, 'bold': True, 'align': 'left', 'valign': 'vcenter'})

        # Ancho de columnas en pulgadas → Excel usa ≈ 10.71 unidades por pulgada
        ancho_columnas = [0.5*inch, 1*inch, 3*inch, 1*inch, 1*inch]
        col_widths = [round(i, 2) for i in ancho_columnas]
        for col, width in enumerate(col_widths):
            worksheet.set_column(col, col, width)

        # -------------------------
        # CONTENIDO DE LA TABLA
        # -------------------------

        data = [
            ["PARA:", "", "SR(A). ALEJANDRA BARRAGAN", "", ""],
            ["", "", "DIRECTORA ADMINISTRATIVA", "", ""],
            ["DE:", "", "RECEPCIÓN", "", ""],
            ["", "", "", "", ""],
            ["ASUNTO:", "", "ENTREGA INFORME MENSUAL", "", ""],
            ["FECHA:", "", fecha_actual_str, "", ""],
            ["Cordial saludo:", "", "", "", ""],
            [f"INFORME CARGA HORARIA MENSUAL DEL {fecha_mes_str} al {ultimo_dia_str}", "", f"Mediante la presente me dirijo a su persona para hacerle entrega de informe mensual correspondiente al mes de {mes_string} de {ano_actual} del Departamento Tutorial, el mismo que se detalla a continuación:", "", ""],
        ]

        # -------------------------
        # ESCRIBIR Y COMBINAR CELDAS
        # -------------------------

        # Función para simplificar escritura y combinación
        def write_merge(row, col1, col2, text, format):
            worksheet.merge_range(row, col1, row, col2, text, format)

        for row_idx, row in enumerate(data):
            if row_idx in [0, 2, 4, 5, 6, 7]:
                write_merge(row_idx, 0, 1, row[0], formato_negrita if row_idx < 6 else formato_cuerpo)
                write_merge(row_idx, 2, 4, row[2], formato_negrita if row_idx < 6 else formato_cuerpo)
            elif row_idx == 1:
                write_merge(row_idx, 2, 4, row[2], formato_negrita)
            elif row_idx == 3:
                pass  # Fila vacía

        # Ajustar alto de filas (opcional, pero ayuda visualmente)
        for i in range(len(data)):
            worksheet.set_row(i, 1*inch)  # altura en puntos (1 pulgada ≈ 72 puntos)

        color_titulos_tabla = '#4472C4'

        formato_titulo_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'bold': True,
            'font_name': 'Helvetica',  # XlsxWriter usa fuentes del sistema, "Helvetica" si está disponible
            'font_color': 'white',
            'bg_color': color_titulos_tabla,
            'text_wrap': True,
            'border': 1
        })

        # Estilo para cuerpo de la tabla
        formato_cuerpo_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'left',
            'valign': 'vcenter',
            'font_color': 'black',
            'text_wrap': True,
            'border': 1
        })

        # Estilo para cantidades (centrado)
        formato_cantidad_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'black',
            'text_wrap': True,
            'border': 1
        })

        formato_final_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'black',
            'bg_color': '#FFFF00',
            'text_wrap': True,
            'border': 1
        })

        fila = 9
        fila_dat = 8


        # ------------------------------ tabla no expirados ----------------------------------------
        worksheet.write(fila, 0, "", formato_titulo_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "DETALLE ESTUDIANTES NO EXPIRADOS", formato_titulo_tabla)
        worksheet.write(fila, 3, "NÚMERO DE ESTUDIANTES", formato_titulo_tabla)
        worksheet.write(fila, 4, "OBSERVACIONES", formato_titulo_tabla)

        fila = fila + 1

        worksheet.write(fila, 0, "", formato_cantidad_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "Estudiantes No Expirados Nivel BASICO", formato_cuerpo_tabla)
        worksheet.write(fila, 3, f"{cantidad_estudiantes_no_expirados_basico}", formato_cantidad_tabla)
        worksheet.write(fila, 4, "", formato_cantidad_tabla)

        fila = fila + 1

        worksheet.write(fila, 0, "", formato_cantidad_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "Estudiantes No Expirados Nivel INTERMEDIO", formato_cuerpo_tabla)
        worksheet.write(fila, 3, f"{cantidad_estudiantes_no_expirados_intermedio}", formato_cantidad_tabla)
        worksheet.write(fila, 4, "", formato_cantidad_tabla)

        fila = fila + 1

        worksheet.write(fila, 0, "", formato_cantidad_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "Estudiantes No Expirados Nivel AVANZADO", formato_cuerpo_tabla)
        worksheet.write(fila, 3, f"{cantidad_estudiantes_no_expirados_avanzado}", formato_cantidad_tabla)
        worksheet.write(fila, 4, "", formato_cantidad_tabla)

        fila = fila + 1

        worksheet.write(fila, 0, "", formato_titulo_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "TOTAL ESTUDIANTES", formato_titulo_tabla)
        worksheet.write(fila, 3, f"{total_no_expirados}", formato_titulo_tabla)
        worksheet.write(fila, 4, "", formato_titulo_tabla)

        fila = fila + 1

        worksheet.merge_range(fila, 0, fila, 4, f"Son {total_no_expirados} estudiantes que realizan sus reservas y se toman en cuenta como activos", formato_final_tabla)
        
        fila = fila + 2

        # -------------------- tabla expirados --------------------------

        worksheet.write(fila, 0, "", formato_titulo_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "DETALLE ESTUDIANTES EXPIRADOS", formato_titulo_tabla)
        worksheet.write(fila, 3, "NÚMERO DE ESTUDIANTES", formato_titulo_tabla)
        worksheet.write(fila, 4, "OBSERVACIONES", formato_titulo_tabla)

        fila = fila + 1

        worksheet.write(fila, 0, "", formato_cantidad_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "Estudiantes Expirados Nivel BASICO", formato_cuerpo_tabla)
        worksheet.write(fila, 3, f"{cantidad_estudiantes_expirados_basico}", formato_cantidad_tabla)
        worksheet.write(fila, 4, "", formato_cantidad_tabla)

        fila = fila + 1

        worksheet.write(fila, 0, "", formato_cantidad_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "Estudiantes Expirados Nivel INTERMEDIO", formato_cuerpo_tabla)
        worksheet.write(fila, 3, f"{cantidad_estudiantes_expirados_intermedio}", formato_cantidad_tabla)
        worksheet.write(fila, 4, "", formato_cantidad_tabla)

        fila = fila + 1

        worksheet.write(fila, 0, "", formato_cantidad_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "Estudiantes Expirados Nivel AVANZADO", formato_cuerpo_tabla)
        worksheet.write(fila, 3, f"{cantidad_estudiantes_expirados_avanzado}", formato_cantidad_tabla)
        worksheet.write(fila, 4, "", formato_cantidad_tabla)

        fila = fila + 1

        worksheet.write(fila, 0, "", formato_titulo_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "TOTAL ESTUDIANTES", formato_titulo_tabla)
        worksheet.write(fila, 3, f"{total_expirados}", formato_titulo_tabla)
        worksheet.write(fila, 4, "", formato_titulo_tabla)

        fila = fila + 1

        worksheet.merge_range(fila, 0, fila, 4, f"Son {total_expirados} estudiantes que tienen contrato expirado", formato_final_tabla)
        
        fila = fila + 2


        # -------------------------- tabla estudiantes nuevos welcomes --------------------------



        worksheet.write(fila, 0, "", formato_titulo_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "DETALLE ESTUDIANTES WELCOME", formato_titulo_tabla)
        worksheet.write(fila, 3, "NÚMERO DE ESTUDIANTES", formato_titulo_tabla)
        worksheet.write(fila, 4, "OBSERVACIONES", formato_titulo_tabla)

        fila = fila + 1


        worksheet.write(fila, 0, "", formato_cantidad_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "WELCOME", formato_cuerpo_tabla)
        worksheet.write(fila, 3, f"{cantidad_estudiantes_nuevos}", formato_cantidad_tabla)
        worksheet.write(fila, 4, "", formato_cantidad_tabla)


        fila = fila + 1

        worksheet.merge_range(fila, 0, fila, 4, f"Estudiantes Nuevos", formato_final_tabla)
        
        fila = fila + 2


        # ---------------------------- tabla estudiantes concluidos -----------------------------------


        worksheet.write(fila, 0, "", formato_titulo_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "DETALLE ESTUDIANTES QUE CONLUYERON EL PROGRAMA", formato_titulo_tabla)
        worksheet.write(fila, 3, "NÚMERO DE ESTUDIANTES", formato_titulo_tabla)
        worksheet.write(fila, 4, "OBSERVACIONES", formato_titulo_tabla)

        fila = fila + 1

        worksheet.write(fila, 0, "", formato_cantidad_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "Estudiantes que terminaron", formato_cuerpo_tabla)
        worksheet.write(fila, 3, f"{cantidad_estudiantes_concluidos}", formato_cantidad_tabla)
        worksheet.write(fila, 4, "", formato_cantidad_tabla)

        
        fila = fila + 2


        # -------------------------- tabla depurados ---------------------------

        worksheet.write(fila, 0, "", formato_titulo_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "DETALLE ESTUDIANTES DEPURADOS", formato_titulo_tabla)
        worksheet.write(fila, 3, "NÚMERO DE ESTUDIANTES", formato_titulo_tabla)
        worksheet.write(fila, 4, "OBSERVACIONES", formato_titulo_tabla)

        fila = fila + 1

        worksheet.write(fila, 0, "", formato_cantidad_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "Estudiantes Depurados Nivel BASICO", formato_cuerpo_tabla)
        worksheet.write(fila, 3, f"{cantidad_estudiantes_depurados_basico}", formato_cantidad_tabla)
        worksheet.write(fila, 4, "", formato_cantidad_tabla)

        fila = fila + 1

        worksheet.write(fila, 0, "", formato_cantidad_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "Estudiantes Depurados Nivel INTERMEDIO", formato_cuerpo_tabla)
        worksheet.write(fila, 3, f"{cantidad_estudiantes_depurados_intermedio}", formato_cantidad_tabla)
        worksheet.write(fila, 4, "", formato_cantidad_tabla)

        fila = fila + 1

        worksheet.write(fila, 0, "", formato_cantidad_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "Estudiantes Depurados Nivel AVANZADO", formato_cuerpo_tabla)
        worksheet.write(fila, 3, f"{cantidad_estudiantes_depurados_avanzado}", formato_cantidad_tabla)
        worksheet.write(fila, 4, "", formato_cantidad_tabla)

        fila = fila + 1

        worksheet.write(fila, 0, "", formato_titulo_tabla)
        worksheet.merge_range(fila, 1, fila, 2, "TOTAL ESTUDIANTES", formato_titulo_tabla)
        worksheet.write(fila, 3, f"{total_depurados}", formato_titulo_tabla)
        worksheet.write(fila, 4, "", formato_titulo_tabla)

        fila = fila + 1

        worksheet.merge_range(fila, 0, fila, 4, f"Son {total_depurados} estudiantes que tienen su contrato expirado del mes de {mes_depurado_uno}, {mes_depurado_dos} y {mes_depurado_tres} con los cuales se comunico en su momento.", formato_final_tabla)
        
        fila = fila + 2
        



        workbook.close()
        buffer.seek(0)

        return buffer
    

    def generar_informe_carga_horaria_docentes_mes_excel(nombre_usuario, fecha):

        margin_left = 0.6 * inch
        margin_right = 0.6 * inch
        margin_top = 1.2 * inch  # Deja espacio para el carimbo
        margin_bottom = 1 * inch

        rojo_fuerte = "#FF4C4C"
        naranja_suave =  "#FFD580"
        amarillo_claro = "#FFFF99"
        verde_claro = "#B2F2B2"

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ano_actual = datetime.now().strftime("%Y")

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

        buffer = BytesIO()

        # Crear el Workbook en memoria
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})

        # Agregar una hoja de trabajo con nombre personalizado
        worksheet = workbook.add_worksheet('Informe Carga Horaria')

        # Definir formatos personalizados
        header_format = workbook.add_format({
            'bold': True, 
            'font_color': 'white', 
            'bg_color': '#4CAF50', 
            'align': 'center',
            'valign': 'vcenter'
        })
        cell_format = workbook.add_format({
            'font_color': 'blue', 
            'italic': True
        })
        # Formato para celdas unidas (merge)
        merge_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#ffffff'
        })



        # Estilos
        formato_inicio = workbook.add_format({'font_size': 8, 'align': 'left', 'valign': 'vcenter'})
        formato_cuerpo = workbook.add_format({'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
        formato_negrita = workbook.add_format({'font_size': 8, 'bold': True, 'align': 'left', 'valign': 'vcenter'})

        # Ancho de columnas en pulgadas → Excel usa ≈ 10.71 unidades por pulgada
        ancho_columnas = [2*inch, 0.8*inch, 2*inch, 0.8*inch, 1.4*inch]
        col_widths = [round(i, 2) for i in ancho_columnas]
        for col, width in enumerate(col_widths):
            worksheet.set_column(col, col, width)

        # -------------------------
        # CONTENIDO DE LA TABLA
        # -------------------------

        data = [
            ["PARA:", "SR(A). CARLA VACAFLORES", "", "", ""],
            ["", "DIRECTORA GENERAL", "", "", ""],
            ["DE:", "RECEPCIÓN", "", "", ""],
            ["", "", "", "", ""],
            ["ASUNTO:", f"ENTREGA INFORME MENSUAL {mes_string}", "", "", ""],
            ["FECHA:", fecha_actual_str, "", "", ""],
            ["Cordial saludo:", "", "", "", ""],
            [f"INFORME CARGA HORARIA MENSUAL DEL {fecha_mes_str} al {ultimo_dia_str}", f"Mediante la presente me dirijo a su persona para hacerle entrega de informe mensual correspondiente al mes de {mes_string} de {ano_actual} del Departamento Tutorial, el mismo que se detalla a continuación:", "", "", ""],
        ]

        # -------------------------
        # ESCRIBIR Y COMBINAR CELDAS
        # -------------------------

        # Función para simplificar escritura y combinación
        def write_merge(row, col1, col2, text, format):
            worksheet.merge_range(row, col1, row, col2, text, format)

        for row_idx, row in enumerate(data):
            if row_idx in [0, 2, 4, 5, 6, 7]:
                worksheet.write(row_idx, 0, row[0], formato_negrita if row_idx < 6 else formato_cuerpo)
                #write_merge(row_idx, 0, 0, row[0], formato_negrita if row_idx < 6 else formato_cuerpo)
                write_merge(row_idx, 1, 4, row[1], formato_negrita if row_idx < 6 else formato_cuerpo)
            elif row_idx == 1:
                write_merge(row_idx, 1, 4, row[1], formato_negrita)
            elif row_idx == 3:
                pass  # Fila vacía

        # Ajustar alto de filas (opcional, pero ayuda visualmente)
        for i in range(len(data)):
            worksheet.set_row(i, 1*inch)  # altura en puntos (1 pulgada ≈ 72 puntos)







        color_titulos_tabla = '#4472C4'

        formato_titulo_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'bold': True,
            'font_name': 'Helvetica',  # XlsxWriter usa fuentes del sistema, "Helvetica" si está disponible
            'font_color': 'white',
            'bg_color': color_titulos_tabla,
            'text_wrap': True,
            'border': 1
        })

        # Estilo para cuerpo de la tabla
        formato_cuerpo_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'black',
            'text_wrap': True,
            'bold': True,
            'border': 1
        })

        # Estilo para cantidades (centrado)
        formato_cantidad_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'black',
            'text_wrap': True,
            'border': 1
        })

        formato_nombre_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'left',
            'valign': 'vcenter',
            'bold': True,
            'font_color': 'black',
            'bg_color': '#FFFFFF',
            'text_wrap': True
        })

        formato_final_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'black',
            'bg_color': '#FFFF00',
            'text_wrap': True,
            'border': 1
        })

        fila = 10
        fila_dat = 9

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

            #fila = fila + 1



            worksheet.merge_range(fila, 0, fila, 4, f"{nombres_docente}", formato_nombre_tabla)

            fila = fila + 1

            worksheet.write(fila, 0, "SEMANA", formato_titulo_tabla)
            worksheet.write(fila, 1, "CARGA HORARIA", formato_titulo_tabla)
            worksheet.write(fila, 2, "TURNO", formato_titulo_tabla)
            worksheet.write(fila, 3, "M/T - T/C", formato_titulo_tabla)
            worksheet.write(fila, 4, "OBSERVACIONES", formato_titulo_tabla)

            fila = fila + 1


            #cabecera = [Paragraph(f"SEMANA", estilo_titulos_tabla), Paragraph(f"CARGA HORARIA", estilo_titulos_tabla), Paragraph(f"TURNO", estilo_titulos_tabla), Paragraph(f"M/T - T/C", estilo_titulos_tabla), Paragraph(f"OBSERVACIONES", estilo_titulos_tabla)]
            
            #tabla_docente.append(cabecera)

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
                
                worksheet.write(fila, 0, f"{dato_string}", formato_cantidad_tabla)
                worksheet.write(fila, 1, f"{dato_t[1]} hrs", formato_cantidad_tabla)
                worksheet.write(fila, 2, "Mañana Tarde Noche", formato_cantidad_tabla)
                worksheet.write(fila, 3, "M/T - T/C", formato_cantidad_tabla)
                worksheet.write(fila, 4, f"Semana {dato_t[2]}", formato_cantidad_tabla)

                fila = fila + 1
                
                #fila_pd = [Paragraph(f"{dato_string}", estilo_cantidad_tabla), Paragraph(f"{dato_t[1]} hrs", estilo_cantidad_tabla), Paragraph(f"Mañana Tarde Noche", estilo_cantidad_tabla), Paragraph(f"M/T - T/C", estilo_cantidad_tabla), Paragraph(f"Semana {dato_t[2]}", estilo_cantidad_tabla)]
                #tabla_docente.append(fila_pd)
            
            worksheet.write(fila, 0, f"TOTAL HORAS TRABAJADAS", formato_cuerpo_tabla)
            worksheet.write(fila, 1, f"{horas_totales} hrs", formato_cuerpo_tabla)
            worksheet.write(fila, 2, "", formato_cuerpo_tabla)
            worksheet.write(fila, 3, "", formato_cuerpo_tabla)
            worksheet.write(fila, 4, "", formato_cuerpo_tabla)

            fila = fila + 2
            
            
            #final = [Paragraph(f"TOTAL HORAS TRABAJADAS", estilo_cuerpo_tabla), Paragraph(f"{horas_totales} hrs", estilo_cuerpo_tabla), '', '', '']
                
            #tabla_docente.append(final)

            #tabla_docente_pdf = Table(tabla_docente, colWidths=ancho_columnas_carga)
            #tabla_docente_pdf.setStyle(estilo_tabla_datos_est)

            #tabla_nombre = Table([[Paragraph(f"{nombres_docente}", estilo_titulo_nombre)]], colWidths=ancho_columnas_total)

            '''elementos.append(tabla_nombre)
            elementos.append(Spacer(1, 10))
            elementos.append(tabla_docente_pdf)
            elementos.append(Spacer(1, 20))

            contador_tablas = contador_tablas + 1
            if contador_tablas == 2:
                elementos.append(PageBreak())
            elif (contador_tablas-5>0 and contador_tablas%3==2):
                elementos.append(PageBreak())'''
        

        workbook.close()
        buffer.seek(0)

        return buffer




    def generar_informe_carga_horaria_docentes_semana_excel(nombre_usuario, fecha):

        margin_left = 0.6 * inch
        margin_right = 0.6 * inch
        margin_top = 1.2 * inch  # Deja espacio para el carimbo
        margin_bottom = 1 * inch

        rojo_fuerte = "#FF4C4C"
        naranja_suave =  "#FFD580"
        amarillo_claro = "#FFFF99"
        verde_claro = "#B2F2B2"

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ano_actual = datetime.now().strftime("%Y")

        fecha_objetivo = datetime.strptime(fecha, "%Y-%m-%d")

        mes_actual = fecha_objetivo.date()
        dias_al_lunes = mes_actual.weekday()
        mes_actual = mes_actual - timedelta(days=dias_al_lunes)
        #mes_actual = mes_actual.replace(day=1)

        fecha_no_expirados = mes_actual + timedelta(days=6)
      
        fecha_actual = datetime.now()

        fecha_actual_str = fecha_actual.strftime("%d/%m/%Y")
        mes_string = MES_INGLES[mes_actual.strftime("%B")]
        fecha_mes_str = mes_actual.strftime("%d/%m/%Y")
        ultimo_dia = fecha_no_expirados - timedelta(days=1)
        ultimo_dia_str = ultimo_dia.strftime("%d/%m/%Y")

        buffer = BytesIO()

        # Crear el Workbook en memoria
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})

        # Agregar una hoja de trabajo con nombre personalizado
        worksheet = workbook.add_worksheet('Informe Carga Horaria')

        # Definir formatos personalizados
        header_format = workbook.add_format({
            'bold': True, 
            'font_color': 'white', 
            'bg_color': '#4CAF50', 
            'align': 'center',
            'valign': 'vcenter'
        })
        cell_format = workbook.add_format({
            'font_color': 'blue', 
            'italic': True
        })
        # Formato para celdas unidas (merge)
        merge_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#ffffff'
        })



        # Estilos
        formato_inicio = workbook.add_format({'font_size': 8, 'align': 'left', 'valign': 'vcenter'})
        formato_cuerpo = workbook.add_format({'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
        formato_negrita = workbook.add_format({'font_size': 8, 'bold': True, 'align': 'left', 'valign': 'vcenter'})

        # Ancho de columnas en pulgadas → Excel usa ≈ 10.71 unidades por pulgada
        ancho_columnas = [0.7*inch, 1.4*inch, 0.7*inch, 1.3*inch, 0.7*inch, 2*inch]
        col_widths = [round(i, 2) for i in ancho_columnas]
        for col, width in enumerate(col_widths):
            worksheet.set_column(col, col, width)

        # -------------------------
        # CONTENIDO DE LA TABLA
        # -------------------------

        data = [
            ["PARA:", "", "SR(A). CARLA VACAFLORES", "", ""],
            ["", "", "DIRECTORA GENERAL", "", ""],
            ["DE:", "", "RECEPCIÓN", "", ""],
            ["", "", "", "", ""],
            ["ASUNTO:", "", f"ENTREGA INFORME SEMANAL", "", ""],
            ["FECHA:", "", fecha_actual_str, "", ""],
            ["Cordial saludo:", "", "", "", ""],
            [f"INFORME CARGA HORARIA SEMANAL DEL  {fecha_mes_str} al {ultimo_dia_str}", "", f"Mediante la presente me dirijo a su persona para hacerle entrega de informe semanal del Departamento Tutorial, el mismo que se detalla a continuación:", "", ""],
        ]

        # -------------------------
        # ESCRIBIR Y COMBINAR CELDAS
        # -------------------------

        # Función para simplificar escritura y combinación
        def write_merge(row, col1, col2, text, format):
            worksheet.merge_range(row, col1, row, col2, text, format)

        for row_idx, row in enumerate(data):
            if row_idx in [0, 2, 4, 5, 6, 7]:
                #worksheet.write(row_idx, 0, row[0], formato_negrita if row_idx < 6 else formato_cuerpo)
                write_merge(row_idx, 0, 1, row[0], formato_negrita if row_idx < 6 else formato_cuerpo)
                write_merge(row_idx, 2, 4, row[2], formato_negrita if row_idx < 6 else formato_cuerpo)
            elif row_idx == 1:
                write_merge(row_idx, 2, 4, row[2], formato_negrita)
            elif row_idx == 3:
                pass  # Fila vacía

        # Ajustar alto de filas (opcional, pero ayuda visualmente)
        for i in range(len(data)):
            worksheet.set_row(i, 1*inch)  # altura en puntos (1 pulgada ≈ 72 puntos)







        color_titulos_tabla = '#4472C4'

        formato_titulo_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'bold': True,
            'font_name': 'Helvetica',  # XlsxWriter usa fuentes del sistema, "Helvetica" si está disponible
            'font_color': 'white',
            'bg_color': color_titulos_tabla,
            'text_wrap': True,
            'border': 1
        })

        # Estilo para cuerpo de la tabla
        formato_cuerpo_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'black',
            'text_wrap': True,
            'bold': True,
            'border': 1
        })

        # Estilo para cantidades (centrado)
        formato_cantidad_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'black',
            'text_wrap': True,
            'border': 1
        })

        formato_nombre_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'left',
            'valign': 'vcenter',
            'bold': True,
            'font_color': 'black',
            'bg_color': '#FFFFFF',
            'text_wrap': True
        })

        formato_final_tabla = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'black',
            'bg_color': '#FFFF00',
            'text_wrap': True,
            'border': 1
        })

        fila = 10
        fila_dat = 9

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

            worksheet.merge_range(fila, 0, fila, 5, f"{nombres_docente}", formato_nombre_tabla)

            fila = fila + 1

            worksheet.write(fila, 0, "DIA", formato_titulo_tabla)
            worksheet.write(fila, 1, "FECHA", formato_titulo_tabla)
            worksheet.write(fila, 2, "CARGA HORARIA", formato_titulo_tabla)
            worksheet.write(fila, 3, "TURNO", formato_titulo_tabla)
            worksheet.write(fila, 4, "M/T - T/C", formato_titulo_tabla)
            worksheet.write(fila, 5, "OBSERVACIONES", formato_titulo_tabla)

            fila = fila + 1


            #cabecera = [Paragraph(f"DIA", estilo_titulos_tabla), Paragraph(f"FECHA", estilo_titulos_tabla), Paragraph(f"CARGA HORARIA", estilo_titulos_tabla), Paragraph(f"TURNO", estilo_titulos_tabla), Paragraph(f"M/T - T/C", estilo_titulos_tabla), Paragraph(f"OBSERVACIONES", estilo_titulos_tabla)]
            
            #tabla_docente.append(cabecera)

            horas_totales = 0

            for dato_t in datos_tabla:
                inicio_s = dato_t[0]
                horas_totales = horas_totales + dato_t[1]

                #semanas = Paragraph(f"{inicio_s}", estilo_cantidad_tabla)
                
                dia_ini = inicio_s.split('-')[0]
                dato_string = f"{dia_ini} de {mes_string} de {ano_actual}"

                fecha_objt = datetime.strptime(inicio_s, "%d-%m-%Y")


                dia_string = DIAS_INGLES[fecha_objt.strftime("%A")]

                worksheet.write(fila, 0, f"{dia_string}", formato_cantidad_tabla)
                worksheet.write(fila, 1, f"{dato_string}", formato_cantidad_tabla)
                worksheet.write(fila, 2, f"{dato_t[1]} hrs", formato_cantidad_tabla)
                worksheet.write(fila, 3, "Mañana Tarde Noche", formato_cantidad_tabla)
                worksheet.write(fila, 4, "M/T - T/C", formato_cantidad_tabla)
                worksheet.write(fila, 5, "", formato_cantidad_tabla)

                fila = fila + 1

                
                #fila_pd = [Paragraph(f"{dia_string}", estilo_cantidad_tabla), Paragraph(f"{dato_string}", estilo_cantidad_tabla), Paragraph(f"{dato_t[1]} hrs", estilo_cantidad_tabla), Paragraph(f"Mañana Tarde Noche", estilo_cantidad_tabla), Paragraph(f"M/T - T/C", estilo_cantidad_tabla), Paragraph(f"", estilo_cantidad_tabla)]
                #tabla_docente.append(fila_pd)
            
            worksheet.merge_range(fila, 0, fila, 1, "TOTAL HORAS TRABAJADAS", formato_cuerpo_tabla)
            #worksheet.write(fila, 0, f"TOTAL HORAS TRABAJADAS", formato_cuerpo_tabla)
            #worksheet.write(fila, 1, "", formato_cuerpo_tabla)
            worksheet.write(fila, 2, f"{horas_totales} hrs", formato_cuerpo_tabla)
            worksheet.write(fila, 3, "", formato_cuerpo_tabla)
            worksheet.write(fila, 4, "", formato_cuerpo_tabla)
            worksheet.write(fila, 5, "", formato_cuerpo_tabla)

            fila = fila + 2

            '''final = [Paragraph(f"TOTAL HORAS TRABAJADAS", estilo_cuerpo_tabla), '', Paragraph(f"{horas_totales} hrs", estilo_cuerpo_tabla), '', '', '']
                
            tabla_docente.append(final)

            tabla_docente_pdf = Table(tabla_docente, colWidths=ancho_columnas_carga)
            tabla_docente_pdf.setStyle(estilo_tabla_datos_est)

            tabla_nombre = Table([[Paragraph(f"{nombres_docente}", estilo_titulo_nombre)]], colWidths=ancho_columnas_total)

            elementos.append(tabla_nombre)
            elementos.append(Spacer(1, 10))
            elementos.append(tabla_docente_pdf)
            elementos.append(Spacer(1, 20))'''
        

        workbook.close()
        buffer.seek(0)

        return buffer
    


    def generar_informe_carga_horaria_docentes_semana_detallado_excel(nombre_usuario, fecha):

        color_titulos_tabla = '#A7C7E7'


        buffer = BytesIO()

        # Crear el Workbook en memoria
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})

        # Agregar una hoja de trabajo con nombre personalizado
        worksheet = workbook.add_worksheet('Informe Carga Horaria Detallado')

        ancho_columnas = [0.7*inch,
                          0.9*inch, 0.9*inch, 0.2*inch, 0.1*inch, 0.2*inch,
                          0.9*inch, 0.9*inch, 0.2*inch, 0.1*inch, 0.2*inch,
                          0.9*inch, 0.9*inch, 0.2*inch, 0.1*inch, 0.2*inch,
                          0.9*inch, 0.9*inch, 0.2*inch, 0.1*inch, 0.2*inch,
                          0.9*inch, 0.9*inch, 0.2*inch, 0.1*inch, 0.2*inch,
                          0.9*inch, 0.9*inch, 0.2*inch, 0.1*inch, 0.2*inch,
                          0.7*inch]
        col_widths = [round(i, 2) for i in ancho_columnas]
        for col, width in enumerate(col_widths):
            worksheet.set_column(col, col, width)

        formato_titulo_tutor = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'bold': True,
            'font_name': 'Helvetica',  # XlsxWriter usa fuentes del sistema, "Helvetica" si está disponible
            'font_color': 'white',
            'bg_color': '#0000FF',
            'text_wrap': True,
            'border': 1
        })

        formato_titulo_total = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'bold': True,
            'font_name': 'Helvetica',  # XlsxWriter usa fuentes del sistema, "Helvetica" si está disponible
            'font_color': 'white',
            'bg_color': '#FF0000',
            'text_wrap': True,
            'border': 1
        })

        formato_cuerpo_1 = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'bold': False,
            'font_name': 'Helvetica',  # XlsxWriter usa fuentes del sistema, "Helvetica" si está disponible
            'font_color': 'black',
            'bg_color': '#FFFFFF',
            'text_wrap': True,
            'border': 1
        })

        formato_cuerpo_2 = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'bold': False,
            'font_name': 'Helvetica',  # XlsxWriter usa fuentes del sistema, "Helvetica" si está disponible
            'font_color': 'black',
            'bg_color': color_titulos_tabla,
            'text_wrap': True,
            'border': 1
        })

        formato_cuerpo_vacio = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'bold': False,
            'font_name': 'Helvetica',  # XlsxWriter usa fuentes del sistema, "Helvetica" si está disponible
            'font_color': 'black',
            'bg_color': '#FF0000',
            'text_wrap': True,
            'border': 1
        })

        

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

        
        

        #estilo_titulos_tabla = ParagraphStyle('titulo_tabla', fontSize=6, alignment=1, fontName="Helvetica-Bold", textColor=colors.white)
        #estilo_cantidad_tabla = ParagraphStyle('cantidad_tabla', fontSize=6, alignment=1, textColor=colors.black)


        lista_horas = ['07:30', '08:30', '09:30', '10:30', '11:30', '12:30', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00']

        docentes = Docente.query.filter(Docente.activo==1).all()

        

        flag_color = True

        
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



        fila = 2

        worksheet.write(fila, 0, "TUTOR", formato_titulo_tutor)

        worksheet.write(fila, 1, "HORA", formato_titulo_total)
        worksheet.merge_range(fila, 2, fila, 5, f"LUNES {fecha_lunes_s}", formato_titulo_total)

        worksheet.write(fila, 6, "HORA", formato_titulo_tutor)
        worksheet.merge_range(fila, 7, fila, 10, f"MARTES {fecha_martes_s}", formato_titulo_tutor)

        worksheet.write(fila, 11, "HORA", formato_titulo_total)
        worksheet.merge_range(fila, 12, fila, 15, f"MIERCOLES {fecha_miercoles_s}", formato_titulo_total)

        worksheet.write(fila, 16, "HORA", formato_titulo_tutor)
        worksheet.merge_range(fila, 17, fila, 20, f"JUEVES {fecha_jueves_s}", formato_titulo_tutor)

        worksheet.write(fila, 21, "HORA", formato_titulo_total)
        worksheet.merge_range(fila, 22, fila, 25, f"VIERNES {fecha_viernes_s}", formato_titulo_total)

        worksheet.write(fila, 26, "HORA", formato_titulo_tutor)
        worksheet.merge_range(fila, 27, fila, 30, f"SABADO {fecha_sabado_s}", formato_titulo_tutor)

        worksheet.write(fila, 31, "TOTAL", formato_titulo_total)

        fila = fila + 1

        contador_celdas = fila - 1


        #cabecera = [Paragraph(f"TUTOR", estilo_titulos_tabla), Paragraph(f"HORA", estilo_titulos_tabla), Paragraph(f"LUNES {dia_numero}", estilo_titulos_tabla), '', Paragraph(f"HORA", estilo_titulos_tabla), Paragraph(f"MARTES {dia_numero+1}", estilo_titulos_tabla), '', Paragraph(f"HORA", estilo_titulos_tabla), Paragraph(f"MIERCOLES {dia_numero+2}", estilo_titulos_tabla), '', Paragraph(f"HORA", estilo_titulos_tabla), Paragraph(f"JUEVES {dia_numero+3}", estilo_titulos_tabla), '', Paragraph(f"HORA", estilo_titulos_tabla), Paragraph(f"VIERNES {dia_numero+4}", estilo_titulos_tabla), '', Paragraph(f"HORA", estilo_titulos_tabla), Paragraph(f"SABADO {dia_numero+5}", estilo_titulos_tabla), '', Paragraph(f"TOTAL", estilo_titulos_tabla)]

        #tabla_general.append(cabecera)

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
                                seccion_nivel = str(sesion.seccion) + "\n" + str(sesion.nivel)
                            #seccion_nivel = str(sesion.seccion) + " " + str(sesion.nivel)
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
                #flag_color = not flag_color
                dict_horas = dato_docente[0]
                if len(dict_horas)>0:
                    flag_color = not flag_color
                    # el original era uno atras toda la columna de abajo
                    list_dias = dato_docente[1]
                    nombre_doc = dato_docente[2]
                    totales = dato_docente[3]
                    inicio_span = contador_celdas + 1
                    fin_span = contador_celdas + 1

                    formato_cuerpo_tabla = formato_cuerpo_2

                    if not flag_color:
                        formato_cuerpo_tabla = formato_cuerpo_1

                    #contador_nombre = 0
                    for hora_d in lista_horas:
                        if hora_d in dict_horas:
                            #contador_nombre = contador_nombre + 1
                            
                            contador_celdas = contador_celdas + 1
                            fin_span = contador_celdas
                            
                            fila_datt = []
                            #if contador_nombre == 1:
                            contador_columna = 1

                            #fila_datt.append(Paragraph(f"{nombre_doc}", estilo_cantidad_tabla))
                            #worksheet.merge_range(inicio_span, 0, fin_span, 0, f"{nombre_doc}", formato_cuerpo_tabla)
                            for dia_l in list_dias:
                                if hora_d in dia_l:
                                    worksheet.write(fila, contador_columna, f"{hora_d}", formato_cuerpo_tabla)
                                    contador_columna = contador_columna + 1
                                    worksheet.write(fila, contador_columna, f"{dia_l[hora_d][0]}", formato_cuerpo_tabla)
                                    contador_columna = contador_columna + 1
                                    cantidad_alumnos = str(dia_l[hora_d][1])
                                    cantidad_asistio = cantidad_alumnos.split('/')[0]
                                    cantidad_total = cantidad_alumnos.split('/')[1]
                                    
                                    if int(cantidad_asistio)==0:
                                        worksheet.write(fila, contador_columna, f"{cantidad_asistio}", formato_cuerpo_vacio)
                                        contador_columna = contador_columna + 1
                                    else:
                                        worksheet.write(fila, contador_columna, f"{cantidad_asistio}", formato_cuerpo_tabla)
                                        contador_columna = contador_columna + 1
                                    worksheet.write(fila, contador_columna, "/", formato_cuerpo_tabla)
                                    contador_columna = contador_columna + 1
                                    worksheet.write(fila, contador_columna, f"{cantidad_total}", formato_cuerpo_tabla)
                                    contador_columna = contador_columna + 1
                                    
                                    #fila_datt.append(Paragraph(f"{hora_d}", estilo_cantidad_tabla))
                                    #fila_datt.append(Paragraph(f"{dia_l[hora_d][0]}", estilo_cantidad_tabla))
                                    #fila_datt.append(Paragraph(f"{dia_l[hora_d][1]}", estilo_cantidad_tabla))
                                else:
                                    worksheet.write(fila, contador_columna, f"{hora_d}", formato_cuerpo_tabla)
                                    contador_columna = contador_columna + 1
                                    worksheet.write(fila, contador_columna, "", formato_cuerpo_tabla)
                                    contador_columna = contador_columna + 1
                                    worksheet.write(fila, contador_columna, "", formato_cuerpo_tabla)
                                    contador_columna = contador_columna + 1
                                    worksheet.write(fila, contador_columna, "", formato_cuerpo_tabla)
                                    contador_columna = contador_columna + 1
                                    worksheet.write(fila, contador_columna, "", formato_cuerpo_tabla)
                                    contador_columna = contador_columna + 1

                                    #fila_datt.append(Paragraph(f"{hora_d}", estilo_cantidad_tabla))
                                    #fila_datt.append('')
                                    #fila_datt.append('')
                            fila = fila + 1
                            
                            #fila_datt.append(Paragraph(f"{totales}", estilo_cantidad_tabla))
                            #worksheet.merge_range(inicio_span, 19, fin_span, 19, f"{totales}", formato_cuerpo_tabla)
                            tabla_general.append(fila_datt)
                                    
                    worksheet.merge_range(inicio_span, 0, fin_span, 0, f"{nombre_doc}", formato_cuerpo_tabla)
                    worksheet.merge_range(inicio_span, 31, fin_span, 31, f"{totales}", formato_cuerpo_tabla)
                    lista_spans.append([inicio_span, fin_span, flag_color])
        

        '''contador_spp = 1
        for spanes in lista_spans:
            coloracion_1 = ('BACKGROUND', (0, spanes[0]), (-1, spanes[1]), color_titulos_tabla)
            #coloracion_2 = ('BACKGROUND', (-1, spanes[0]), (-1, spanes[1]), color_titulos_tabla)
            #coloracion_3 = ('BACKGROUND', (1, spanes[0]), (-2, spanes[1]), color_titulos_tabla)
            if contador_spp%2==0:
                estilo_tabla_datos_est.append(coloracion_1)
                #estilo_tabla_datos_est.append(coloracion_2)
                #estilo_tabla_datos_est.append(coloracion_3)
            span_nombre = ('SPAN', (0, spanes[0]), (0, spanes[1]))
            span_total = ('SPAN', (-1, spanes[0]), (-1, spanes[1]))
            
            estilo_tabla_datos_est.append(span_nombre)
            estilo_tabla_datos_est.append(span_total)
            
            contador_spp = contador_spp + 1'''
        
        '''estilo_tabla_datos_est = TableStyle(estilo_tabla_datos_est)
 

        tabla_general_pdf = Table(tabla_general)
        tabla_general_pdf.setStyle(estilo_tabla_datos_est)



        elementos.append(Spacer(1, 20))
        elementos.append(tabla_general_pdf)
        elementos.append(Spacer(1, 20))'''




        

        workbook.close()
        buffer.seek(0)

        return buffer


