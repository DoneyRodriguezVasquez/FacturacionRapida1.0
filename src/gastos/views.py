import os
import traceback
import locale

from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect

from .utils import limpiar_nombre_asunto, crear_carpeta_unica, guardar_adjuntos, obtiene_mensajes, obtiene_compras
from facturacion.xml_handler import Facturas 

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')


class Descarga(View):
    def get(self, request, *args, **kwargs):
        try:
            mensajes_list = [] # Inicializa una lista para almacenar los mensajes procesados

            mensajes = obtiene_mensajes()  # Asegúrate de que esta función devuelve una lista de mensajes

            if not mensajes:
                return render(request, 'carga_factura.html', {'message': 'No hay mensajes en la carpeta "Por confirmar".'})

            # Recorrer los correos en la carpeta "Facturas"
            for mensaje in mensajes:
                # Verificar si tiene adjuntos
                if mensaje.Attachments.Count > 0:

                    fecha_mensaje = mensaje.ReceivedTime
                    numero_mes = fecha_mensaje.strftime("%m")
                    nombre_mes = fecha_mensaje.strftime("%B")
                    nombre_carpeta_mes = f"{numero_mes}-{nombre_mes}"

                    # agregamos los correos a un diccionario
                    mensajes_list.append({
                        'fecha': fecha_mensaje,
                        'proveedor': mensaje.sendername,
                        'carpeta': nombre_carpeta_mes
                    })
            return render(request, 'carga_factura.html', {'mensajes': mensajes_list})

        except Exception as e:
            print(f"Error al descargar adjuntos: {e}")
            import traceback
            traceback.print_exc()
            return render(request, 'carga_factura.html', {'message': 'Ocurrió un error al procesar los mensajes.'})
        
    
    def post(self, request, *args, **kwargs):
        try:
            mensajes = obtiene_mensajes()  # Asegúrate de que esta función devuelve una lista de mensajes

            # Recorrer los correos en la carpeta "Facturas"
            for mensaje in mensajes:
                # Verificar si tiene adjuntos
                if mensaje.Attachments.Count > 0:
                    # Limpiar el nombre del asunto
                    asunto_limpio = limpiar_nombre_asunto(mensaje.Subject)

                    fecha_mensaje = mensaje.ReceivedTime
                    numero_mes = fecha_mensaje.strftime("%m")
                    nombre_mes = fecha_mensaje.strftime("%B")
                    nombre_carpeta_mes = f"{numero_mes}-{nombre_mes}"

                    # Crear una carpeta única para el asunto
                    base_path = 'C:/Users/Innotec 02/OneDrive/Hacienda/Facturas/'
                    asunto_folder = crear_carpeta_unica(base_path, os.path.join(nombre_carpeta_mes, asunto_limpio))

                    # Guardar los adjuntos en la carpeta creada
                    guardar_adjuntos(mensaje, asunto_folder)

            return render(request, 'download_complete.html')
        except Exception as e:
            print(f"Error al descargar adjuntos: {e}")
            import traceback
            traceback.print_exc()
            return render(request, 'carga_factura.html', {'message': str(e)})

class CargaCompras(LoginRequiredMixin, View):
    """
    Se maneja la carga y procesamiento de facturas de compra.
    Requiere que el usuario esté autenticado.
    """
    def get(self, request):
        form = obtiene_compras() 
        return render(request, 'ingresos.html', {'form': form, 'titulo': 'Carga de compras'})

    def post(self, request):
        if 'myFiles' not in request.FILES:
            messages.error(request, 'No se ha cargado el archivo.')
            return HttpResponseRedirect('/gastos/carga_compras')
        
        factura = Facturas(request.FILES['myFiles'], request.user, 'compra')

        if factura.validar():
            try:
                factura.handle_uploaded_file()
            except Exception as e:
                muestra_mensajes(request, factura.errors)  
                print(f"Error al procesar el archivo: {e}")
                traceback.print_exc()
                return HttpResponseRedirect('/gastos/carga_compras')
            
            messages.success(request,'Documento agregado satisfactoriamente.')
            return HttpResponseRedirect('/gastos/carga_compras')
        else:
            muestra_mensajes(request, factura.errors)
            return HttpResponseRedirect('/gastos/carga_compras')

def muestra_mensajes(request, lista_mensajes):
    """
    Muestra los mensajes en la plantilla de carga_factura.html.
    """
    for value in lista_mensajes:
        messages.error(request, value)
    