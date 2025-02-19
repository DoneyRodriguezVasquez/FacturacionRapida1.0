import re
import os
import calendar
import win32com.client

from datetime import datetime
from dateutil.relativedelta import relativedelta

from .models import FacturaGasto, ImpuestoDetalleGasto
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q


def limpiar_nombre_asunto(asunto):
    """
    Limpia el nombre del asunto para que sea un nombre de archivo válido.
    """
    # Reemplazar espacios con guiones bajos
    asunto_limpio = re.sub(r'\s+', '_', asunto)
    # Reemplazar caracteres no permitidos en nombres de archivos
    asunto_limpio = re.sub(r'[<>:"/\\|?*]', '_', asunto_limpio)
    # Reemplazar múltiples guiones bajos consecutivos con uno solo
    asunto_limpio = re.sub(r'_+', '_', asunto_limpio)
    return asunto_limpio

def crear_carpeta_unica(base_path, nombre_carpeta):
    """
    Crea una carpeta única en el sistema de archivos.
    Si la carpeta ya existe, añade un sufijo numérico para hacerla única.
    """
    carpeta = os.path.join(base_path, nombre_carpeta)
    original_carpeta = carpeta
    counter = 1
    while os.path.exists(carpeta):
        carpeta = f"{original_carpeta}_{counter}"
        counter += 1
    os.makedirs(carpeta)
    return carpeta

def guardar_adjuntos(mensaje, carpeta):
    """
    Guarda los archivos adjuntos de un mensaje en la carpeta especificada.
    """
    for adjunto in mensaje.Attachments:
        filename = adjunto.FileName
        if filename and filename.strip():
            filepath = os.path.join(carpeta, filename)
            print(f"Guardando archivo en: {filepath}")
            adjunto.SaveAsFile(filepath)
        else:
            print(f"Nombre de archivo inválido: {filename}")

def obtiene_mensajes():
    """
    Conecta a Outlook y obtiene los mensajes de la carpeta "Por confirmar".
    """
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        inbox = outlook.Folders.Item(1)
        facturas_folder = inbox.Folders.Item("Por confirmar")
        
        # Forzar la actualización de la carpeta
        facturas_folder.Items.Sort("[ReceivedTime]", True)
        facturas_folder.Items.IncludeRecurrences = True

        # Obtener los mensajes en la carpeta 
        mensajes = facturas_folder.Items.Restrict("[MessageClass] = 'IPM.Note'")
        return mensajes
    except Exception as e:
        print(f"Error al conectar con Outlook: {e}")
        return None
    

def obtiene_compras():
    """
    Se obtienen todas las compras de los dos últimos meses para ver las últimas
    facturas que se estan cargando a la base de datos.
    """
    fecha = datetime.today()
    fecha_ini = fecha - relativedelta(months=2)    #se obtiene el primer día de hace 2 meses

    return FacturaGasto.objects.all().filter(
        fecha_emision__range = (fecha_ini, fecha)
    ).order_by('fecha_emision').reverse()

def obtiene_compras_mes_anterior():
    fecha = datetime.today()
    fecha_ini = fecha.replace(month=fecha.month, day=1)   #se obtiene el primer día del mes anterior
    fecha_fin = fecha.replace(month=fecha.month, day = calendar.monthrange(fecha.year, fecha.month-1)[1]) #se obtiene el último día del mes anterior

    return FacturaGasto.objects.all().filter(FechaEmision__range = (fecha_ini, fecha_fin)).order_by('FechaEmision') 
 

def generar_reporte_credito_fiscal(facturas):
    # Agrupar por tipo de compra
    categorias = {
        'con_iva': facturas.filter(lineas_detalle__tipo_compra='con_iva'),
        'sin_iva': facturas.filter(lineas_detalle__tipo_compra='sin_iva'),
        'exento': facturas.filter(lineas_detalle__tipo_compra='exento'),
        'no_acreditable': facturas.filter(lineas_detalle__tipo_compra='no_acreditable')
    }
    
    # Detalle por tipo de impuesto y tarifa
    detalle_impuestos = (
        ImpuestoDetalleGasto.objects
        .filter(linea_detalle__factura_gasto__in=facturas)
        .values('codigo', 'codigo_tarifa', 'tarifa')
        .annotate(
            total_monto=Sum('monto'),
            total_base=Sum('linea_detalle__monto_total_linea')
        )
        .order_by('codigo', 'tarifa')
    )
    
    return {
        'categorias': categorias,
        'detalle_impuestos': detalle_impuestos
    }

def clean(self):
    if self.codigo == '01' and self.tarifa not in [0, 1, 2, 4, 13]:
        raise ValidationError('Tarifa IVA inválida')
    
def calcular_subtotal(self):
    return self.cantidad * self.precio_unitario

def calcular_total(self):
    return self.calcular_subtotal() - self.descuento

def determinar_tipo_compra(self):
    if self.impuestos.filter(codigo='01', codigo_tarifa='01').exists():
        return 'exento'
    # ... otras reglas  
    return 'con_iva'