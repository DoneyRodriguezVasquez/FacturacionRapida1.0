from django.shortcuts import render
from django.views.generic import View

class Home(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')

class Dashboard(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard.html')
