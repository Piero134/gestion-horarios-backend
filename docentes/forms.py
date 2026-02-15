from django import forms
from .models import Docente
from facultades.models import Departamento

class DocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = [
            'tipo', 'dni', 'apellido_paterno', 'apellido_materno', 'nombres',
            'email', 'facultad', 'departamento',
            'codigo', 'categoria', 'dedicacion'
        ]

        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo'}),
            'facultad': forms.Select(attrs={'class': 'form-select select2-facultad', 'id': 'id_facultad'}),
            'departamento': forms.Select(attrs={'class': 'form-select select2-departamento', 'id': 'id_departamento'}),

            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_materno': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'dedicacion': forms.Select(attrs={'class': 'form-select'}),
        }

        labels = {
            'tipo': 'Condición Laboral',
            'email': 'Correo Institucional',
            'departamento': 'Departamento Académico'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['departamento'].queryset = Departamento.objects.none()

        if 'facultad' in self.data:
            try:
                facultad_id = int(self.data.get('facultad'))
                self.fields['departamento'].queryset = Departamento.objects.filter(facultad_id=facultad_id).order_by('nombre')
            except (ValueError, TypeError):
                pass

        elif self.instance.pk and self.instance.facultad:
            self.fields['departamento'].queryset = Departamento.objects.filter(facultad=self.instance.facultad).order_by('nombre')

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')

        if tipo == Docente.TipoDocente.NOMBRADO:
            if not cleaned_data.get('departamento'):
                self.add_error('departamento', 'El departamento es obligatorio para docentes nombrados.')
            if not cleaned_data.get('codigo'):
                self.add_error('codigo', 'El código es obligatorio para docentes nombrados.')
            if not cleaned_data.get('categoria'):
                self.add_error('categoria', 'La categoría es obligatoria.')
            if not cleaned_data.get('dedicacion'):
                self.add_error('dedicacion', 'La dedicación es obligatoria.')

        elif tipo == Docente.TipoDocente.CONTRATADO:
            cleaned_data['codigo'] = None
            cleaned_data['categoria'] = None
            cleaned_data['dedicacion'] = None

        return cleaned_data
