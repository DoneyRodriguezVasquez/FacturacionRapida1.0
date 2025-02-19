from django.db import models

class FacturaServicio(models.Model):
    clave = models.CharField(max_length=100, unique=True)
    codigo_actividad = models.CharField(max_length=10)
    numero_consecutivo = models.CharField(max_length=50)
    fecha_emision = models.DateTimeField()
    emisor_nombre = models.CharField(max_length=255)
    emisor_identificacion = models.CharField(max_length=20)
    receptor_nombre = models.CharField(max_length=255)
    receptor_identificacion = models.CharField(max_length=20)
    total_gravado = models.DecimalField(max_digits=15, decimal_places=2)
    total_impuesto = models.DecimalField(max_digits=15, decimal_places=2)
    total_comprobante = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = 'Ingreso'
        verbose_name_plural = 'Ingresos'
        ordering = ['fecha_emision']    
    
    def __str__(self):
        return f"{self.numero_consecutivo} - {self.fecha_emision} - {self.total_comprobante} - {self.receptor_nombre}"