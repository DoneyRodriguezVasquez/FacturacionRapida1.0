from django import forms
from django.contrib.auth import authenticate
from usuario.models import Usuario


TIPO_ID_CHOICES = (('00','Seleccione'),('01','Persona Física'),('02','Pesona Juridica'))

class UserForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Escriba su contraseña',
            'id': 'password1',
            'required': 'required',
        }
    ))
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Vuelva a escribir su contraseña',
            'id': 'password2',
            'required': 'required',
        }
    ))

    class Meta:
        model = Usuario
        fields = ('email','nombre','apellidos','actividad', 'tipo_identificacion', 'num_identificacion')
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese su email',
                }
            ),
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese su nombre',
                }
            ),
            'apellidos': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese sus apellidos',
                }
            ),
            'actividad': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese el nombre de la actividad',
                }
            ),
            'tipo_identificacion': forms.Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Seleccione el tipo de identificación',
                },
                choices=TIPO_ID_CHOICES
            ),
            'num_identificacion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese su número de identificación',
                }
            ),
        }
        help_text = {k: "" for k in fields } 

    def clean_password2(self):

        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationsError('Las contraseñas no coinciden')
        return password2 

    def save(self, commit=True):
        user = super.save(commit= False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user 


class LoginForm(forms.ModelForm):
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Escriba su contraseña',
            'id': 'password',
            'required': 'required',
        }
    ))

    class Meta:
        model = Usuario
        fields = ('email', 'password')
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese su email',
                }
            ),
        }
    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']

            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Credenciales invalidas")

