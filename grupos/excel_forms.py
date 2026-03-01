from django import forms
from periodos.models import PeriodoAcademico
from escuelas.models import Escuela

class UploadExcelForm(forms.Form):
    periodo = forms.ModelChoiceField(
        queryset=PeriodoAcademico.objects.all().order_by('-nombre'),
        label="Periodo Académico",
        empty_label="Seleccione un periodo...",
        widget=forms.Select(attrs={'class': 'form-control select2-busqueda'})
    )

    escuela = forms.ModelChoiceField(
        queryset=Escuela.objects.none(), # Se llena en el __init__
        label="Escuela Profesional",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    archivo = forms.FileField(
        label="Seleccionar Excel de Programación",
        help_text="El archivo debe contener las columnas ASIGNATURA, GRUPO, DIA, H.INI, H.FIN, DOCENTE",
        widget=forms.FileInput(attrs={
            'accept': '.xlsx, .xls',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['escuela'].queryset = Escuela.objects.para_usuario(user)

            if self.fields['escuela'].queryset.count() == 1:
                self.fields['escuela'].initial = self.fields['escuela'].queryset.first()
                self.fields['escuela'].widget = forms.HiddenInput()

        # Seleccionar automáticamente el periodo activo por defecto
        periodo_activo = PeriodoAcademico.objects.get_activo()
        if periodo_activo:
            self.fields['periodo'].initial = periodo_activo

    def clean_archivo(self):
        file = self.cleaned_data['archivo']
        if not file.name.endswith('.xlsx'):
            raise forms.ValidationError("El archivo debe tener extensión .xlsx")
        return file
