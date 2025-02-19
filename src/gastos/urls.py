from django.urls import path
from gastos.views import Descarga, CargaCompras


urlpatterns = [
    path('descarga/', Descarga.as_view(), name='descarga'),
    path('carga_compras/', CargaCompras.as_view(), name='carga_compras'),
]