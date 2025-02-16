from datetime import datetime
from django.conf import settings
import requests, xmltodict


def obtiene_tipo_cambio():
    """ Para consumir el tipo de cambio de compra se parametriza de la siguiente
        manera: el código es 317; fecha de inicio 01/01/2005 y fecha final 01/01/2005; el
        usuario es "N"; debido a que el tipo de cambio de compra no tiene
        subniveles entonces se define N; correo electrónico y token. 
        Para el tipo de cambio venta su código es 318 y se configura como el de compra. """

    email = settings.EMAIL
    token = settings.TOKEN
    url = settings.URL_API_TC
    compra = 0
    venta = 0
    compra = consume_api(url, 317, email, token)
    venta = consume_api(url, 318, email, token)
    
    return {'compra':compra, 'venta':venta}


def consume_api(url, indicador, email, token):
    valor = 0
    fecha = datetime.today()
    fechaInicio = str(fecha.day) +'/'+str(fecha.month)+'/'+str(fecha.year)
    fechaFinal = str(fecha.day) +'/'+str(fecha.month)+'/'+str(fecha.year)

    params = {
        'FechaInicio': fechaInicio,
        'FechaFinal': fechaFinal,
        'Nombre': 'N',
        'SubNiveles': 'N',
        'Indicador': indicador,
        'CorreoElectronico': email,
        'Token': token,
    }

    respuesta = requests.get(url, params=params)
    if respuesta.status_code == 200:
        obj = xmltodict.parse(respuesta.content)
        xml = obj["string"]["#text"]
        data = xmltodict.parse(xml)
        valor = int(float(data["Datos_de_INGC011_CAT_INDICADORECONOMIC"]["INGC011_CAT_INDICADORECONOMIC"]["NUM_VALOR"]))
    return valor