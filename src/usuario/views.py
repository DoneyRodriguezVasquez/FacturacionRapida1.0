from django.shortcuts import render, redirect
from usuario.forms import UserForm, LoginForm
from django.contrib.auth import login, logout, authenticate 
from django.views.generic import CreateView
from django.contrib.auth import login, logout
from usuario.models import Usuario
from django.http import HttpResponse
from facturacion.scripts import *


class Register(CreateView):
    model = Usuario
    form_class = UserForm
    template_name = 'usuario/register.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            nuevo_usuario = Usuario(
                email = form.cleaned_data.get('email'),
                nombre = form.cleaned_data.get('nombre'),
                apellidos = form.cleaned_data.get('apellidos'),
                actividad = form.cleaned_data.get('actividad'),
                tipo_identificacion = form.cleaned_data.get('tipo_identificacion'),
                num_identificacion = form.cleaned_data.get('num_identificacion')
            )
            nuevo_usuario.set_password(form.cleaned_data.get('password1'))
            nuevo_usuario.save()
            logout(request)
            return redirect('login')
        else:
            return render(request, self.template_name, {'form': form})


def login_view(request):
    context={}
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email=request.POST['email']
            password=request.POST['password']
            user=authenticate(request, email=email, password=password)

            if user is not None:
                tc = obtiene_tipo_cambio()
                login(request, user)
                response = redirect('home:dashboard')
                response.set_cookie('tc_compra', tc['compra'])
                response.set_cookie('tc_venta', tc['venta'])
                return response
    else:
        form=LoginForm()
        context = {'form': form}
    return render(request, 'usuario/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')