from django.db import models
from django.core.validators import MinValueValidator

class FacturaGasto(models.Model):
    clave = models.CharField(max_length=100, unique=True)
    codigo_actividad = models.CharField(max_length=10)
    numero_consecutivo = models.CharField(max_length=50)
    fecha_emision = models.DateTimeField()
    emisor_nombre = models.CharField(max_length=255)
    emisor_identificacion = models.CharField(max_length=20)
    receptor_nombre = models.CharField(max_length=255)
    receptor_identificacion = models.CharField(max_length=20)
    total_venta_neta = models.DecimalField(max_digits=15, decimal_places=2)
    total_impuesto = models.DecimalField(max_digits=15, decimal_places=2)
    total_comprobante = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return self.numero_consecutivo
    
class LineaDetalleGasto(models.Model):
    """
    Modelo para guardar los detalles de las facturas de gastos.
    Se relaciona con el modelo FacturaGasto.
    Se guarda la información de los productos o servicios que se compraron.
    Se guarda la información de los impuestos que se aplicaron a los productos o servicios.
    Se usa para generar un reporte de credito fiscal que se puede deducir en la declaración de impuestos IVA.
    Se desea hacer un reporte que muestre las compras con IVA soportado acreditable, las compras sin IVA soportado y/o
    con IVA soportado no acreditable, y las compras exentas. También se desea mostrar el crédito fiscal por tipo de impuesto 
    y por porcentaje
    """

    factura_gasto = models.ForeignKey(FacturaGasto, on_delete=models.CASCADE, related_name='lineas_detalle')
    numero_linea = models.PositiveSmallIntegerField()
    codigo = models.CharField(max_length=20, blank=True, null=True) # Código del producto o servicio
    nombre = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    unidad_medida = models.CharField(max_length=20)
    precio_unitario = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    monto_total = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    descuento = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    monto_total_linea = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])

    # Campos para clasificacion del reporte 
    TIPO_COMPRA_CHOICES = [
        ('con_iva', 'Con IVA soportado acreditable'),
        ('sin_iva', 'Sin IVA soportado'),
        ('exento', 'Exento'),
        ('no_acreditable', 'IVA no acreditable')
    ]
    tipo_compra = models.CharField(max_length=20, choices=TIPO_COMPRA_CHOICES, default='con_iva')

    def __str__(self):
        return f"Línea {self.numero_linea} - {self.nombre}"

class ImpuestoDetalleGasto(models.Model):
    """ Relacion con la linea de detalle de la factura de gasto.
    Se guarda la información de los impuestos que se aplicaron a los productos o servicios.
    """
    # Código del impuesto
    # 01 = Impuesto General sobre las Ventas
    # 02 = Impuesto Selectivo de Consumo
    # 03 = Impuesto Único a los combustibles
    # 99 = Otros

    CODIGO_IMPUESTO_CHOICES = [
        ('01', 'IVA'),
        ('02', 'ISC'),
        ('03', 'Impuesto Único Combustibles'),
        ('99', 'Otros')
    ]

    CODIGO_TARIFA_IVA_CHOICES = [
        ('01', 'Exento'),
        ('02', '1%'),
        ('03', '2%'),
        ('08', '13%'),
        ('99', 'Otros')
    ]

    linea_detalle = models.ForeignKey(LineaDetalleGasto, on_delete=models.CASCADE, related_name='impuestos')
    codigo = models.CharField(max_length=2, choices=CODIGO_IMPUESTO_CHOICES, default='01')
    codigo_tarifa = models.CharField(max_length=2, choices=CODIGO_TARIFA_IVA_CHOICES, default='08')
    tarifa = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    monto = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"Impuesto {self.get_codigo_display()} - {self.tarifa} - {self.monto}%"
