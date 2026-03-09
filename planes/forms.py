from django import forms
from escuelas.models import Escuela
from planes.models import PlanEstudios

class PlanUploadForm(forms.Form):
    escuela = forms.ModelChoiceField(
        queryset=Escuela.objects.none(),
        label="Escuela Profesional",
        widget=forms.Select(attrs={'class': 'form-select select2-escuela'})
    )
    anio_plan = forms.IntegerField(
        label="Año del Plan",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    archivo_excel = forms.FileField(
        label="Archivo Excel (.xlsx)",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        # Usamos tu Manager personalizado para filtrar las escuelas
        qs_escuelas = Escuela.objects.para_usuario(user)
        self.fields['escuela'].queryset = qs_escuelas

        # Si solo hay una escuela disponible, se selecciona por defecto
        if qs_escuelas.count() == 1:
            self.fields['escuela'].initial = qs_escuelas.first()
            # Opcional: deshabilitar si no quieres que cambie
            self.fields['escuela'].disabled = True

    def clean_archivo_excel(self):
        file = self.cleaned_data.get('archivo_excel')
        if not file.name.endswith('.xlsx'):
            raise forms.ValidationError("Solo se permiten archivos Excel (.xlsx)")
        return file
