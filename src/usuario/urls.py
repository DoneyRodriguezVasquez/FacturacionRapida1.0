from django.urls import path, include
from django.contrib.auth.decorators import login_required
from usuario.views import Register

app_name = 'usuario'

urlpatterns = [
    path('register/', Register.as_view(), name='register' ),
]