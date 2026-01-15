from django.contrib import admin
from .models import Horario

class HorarioInline(admin.TabularInline):
    model = Horario
    extra = 2
    autocomplete_fields = ['aula']
