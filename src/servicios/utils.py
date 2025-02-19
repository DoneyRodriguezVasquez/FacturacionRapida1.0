from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import FacturaServicio



def obtiene_ingresos():
    fecha = datetime.today()
    fecha_ini = fecha - relativedelta(months=6)    #se obtiene el primer día de hace 6 meses
   
    #se filtran los datos de los ingresos de los ultimos 6 meses 
    data = FacturaServicio.objects.all().filter(
        fecha_emision__range = (fecha_ini, fecha)
    ).order_by('fecha_emision')
    return data 