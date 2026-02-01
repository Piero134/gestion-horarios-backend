from django import forms
from .models import Horario
from aulas.models import Aula

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['tipo', 'dia', 'hora_inicio', 'hora_fin', 'aula']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select form-select-sm'
            }),
            'dia': forms.Select(attrs={
                'class': 'form-select form-select-sm'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control form-control-sm',
                'type': 'time'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control form-control-sm',
                'type': 'time'
            }),
            'aula': forms.Select(attrs={
                'class': 'form-select form-select-sm'
            }),
        }
        labels = {
            'tipo': 'Tipo',
            'dia': 'Día',
            'hora_inicio': 'Inicio',
            'hora_fin': 'Fin',
            'aula': 'Aula'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['aula'].queryset = Aula.objects.all().order_by('nombre')
        # self.fields['aula'].queryset = Aula.objects.all().order_by('pabellon', 'numero')

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')

        if hora_inicio and hora_fin:
            if hora_inicio >= hora_fin:
                self.add_error('hora_fin', "La hora de fin debe ser posterior a la de inicio.")

        return cleaned_data
