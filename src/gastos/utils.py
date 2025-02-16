import re
import os
import win32com.client

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