from django.urls import path
from home.views import Home, Dashboard

app_name = 'home'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
]