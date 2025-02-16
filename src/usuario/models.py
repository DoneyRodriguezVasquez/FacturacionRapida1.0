from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    #use_in_migrations = True

    def create_user(self, email, nombre, apellidos, actividad, tipo_identificacion, num_identificacion, password = None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Se debe registrar un email válido')

        user = self.model(
            email = self.normalize_email(email),
            nombre = nombre,
            apellidos = apellidos,
            actividad = actividad,
            tipo_identificacion = tipo_identificacion,
            num_identificacion = num_identificacion
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email,  nombre, apellidos, actividad, tipo_identificacion, num_identificacion, password):
        user = self.create_user(
            email,
            nombre = nombre,
            apellidos = apellidos,
            actividad = actividad,
            tipo_identificacion = tipo_identificacion,
            num_identificacion = num_identificacion,
            password = password
        )
        user.is_staff = True
        user.save()
        return user

 
class Usuario(AbstractBaseUser, PermissionsMixin):
    #username = models.CharField('Usuario', unique=True, max_length=100)
    email = models.EmailField('Email', max_length=200, unique=True)
    nombre = models.CharField('Nombre', max_length=100, blank=False, null=False)
    apellidos = models.CharField('Apellidos', max_length=200, blank=False, null=False)
    actividad = models.CharField('Nombre de Actividad', max_length=200, blank=False, null=False)
    tipo_identificacion = models.CharField('Tipo de identificación', max_length=2, blank=False, null=False)
    num_identificacion = models.CharField('Numero de identificación', max_length=20, blank=False, null=False)
    is_active = models.BooleanField('active', default=True)
    is_staff = models.BooleanField('staff', default=False) 
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellidos', 'actividad', 'tipo_identificacion', 'num_identificacion']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
    
    def __str__(self):
        return f'Email: {self.email} - Nombre completo: {self.nombre} {self.apellidos}' 
        

    def has_perm(self, perm, obj = None):
        return True

    def has_module_perms(self, app_label):
        return True

    """ @property
    def is_staff(self):
        return  self.is_staff"""

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.nombre, self.apellidos)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.nombre

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs) 