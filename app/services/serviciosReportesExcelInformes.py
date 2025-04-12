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


