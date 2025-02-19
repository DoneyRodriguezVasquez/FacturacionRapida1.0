import os
import logging

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .utils import obtiene_ingresos
from facturacion.xml_handler import Facturas 



class CargaServicios(LoginRequiredMixin, View):
    def get(self, request):
        form = obtiene_ingresos() 
        return render(request, 'ingresos.html', {'form': form, 'titulo': 'Carga de servicios'})

    def post(self, request):
        if 'myFiles' not in request.FILES:
            messages.error(request, 'No se ha cargado el archivo.')
            return HttpResponseRedirect('/servicios/carga')
        
        factura = Facturas(request.FILES['myFiles'], request.user, 'servicio')

        if factura.validar():
            try:
                factura.handle_uploaded_file()
            except Exception as e:
                logger = logging.getLogger(__name__)
                print(e)
                logger.error(e)
                return HttpResponseRedirect('/servicios/carga')
            
            for value in factura.errors:
                messages.error(request, value)
            factura.errors.clear()
            return HttpResponseRedirect('/servicios/carga')
        else:
            messages.success(request,'Documento agregado satisfactoriamente.')
            return HttpResponseRedirect('/servicios/carga')     
 
class ReporteServicios(LoginRequiredMixin, View):
    def get(self, request):
        form = obtiene_ingresos() 
        return render(request, 'reporte_ventas.html', {'form': form})

