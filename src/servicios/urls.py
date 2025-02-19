from django.urls import path
from servicios.views import CargaServicios, ReporteServicios


urlpatterns = [
    path('carga/', CargaServicios.as_view(), name='carga_servicios'),
    path('reporte_ventas/', ReporteServicios.as_view(), name='reporte_ventas'),
]