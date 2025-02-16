from django.shortcuts import render
from django.views.generic import View
from .utils import limpiar_nombre_asunto, crear_carpeta_unica, guardar_adjuntos, obtiene_mensajes
import locale
import os

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')


class Carga(View):
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


