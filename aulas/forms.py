from django import forms
from .models import Aula

class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = ['nombre', 'pabellon', 'vacantes', 'tipo_sesion', 'facultad', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 101 NP'}),
            'pabellon': forms.Select(attrs={'class': 'form-select'}),
            'vacantes': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_sesion': forms.Select(attrs={'class': 'form-select'}),
            'facultad': forms.Select(attrs={'class': 'form-select select2-facultad'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            if user.is_superuser:
                # El superusuario puede elegir cualquier facultad
                self.fields['facultad'].required = True
                self.fields['facultad'].help_text = "Busca y selecciona la facultad destino."
            else:
                # Usuario normal: bloqueado a su facultad
                if hasattr(user, 'facultad') and user.facultad:
                    self.fields['facultad'].initial = user.facultad
                    # Usamos readonly y disabled para que no
