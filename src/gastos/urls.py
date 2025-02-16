from django.urls import path
from gastos.views import Carga
from home.views import Dashboard


urlpatterns = [
    path('carga/', Carga.as_view(), name='carga'),
    #path('home/dashboard/', Dashboard.as_view(), name='dashboard'), 
]