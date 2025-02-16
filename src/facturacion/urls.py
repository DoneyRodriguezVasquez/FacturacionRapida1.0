from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from usuario.views import login_view, logout_view 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('home.urls', 'home'))), 
    path('accounts/login/', login_view, name='login'),
    path('logout/', login_required(logout_view), name='logout'),
    path('usuario/', include(('usuario.urls', 'usuarios'))), 
    path('clientes/', include(('clientes.urls', 'clientes'))),
    #path('proveedor/', include(('proveedor.urls', 'proveedor'))),
    path('servicios/', include(('servicios.urls', 'servicios'))),
    path('gastos/', include(('gastos.urls', 'gastos'))),
    path('reportes/', include(('reportes.urls', 'reportes'))),
    #path('api/', include(('api.urls', 'api'))),
]