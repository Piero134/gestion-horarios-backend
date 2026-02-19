from django import forms

class UploadExcelForm(forms.Form):
    archivo = forms.FileField(
        label="Seleccionar Excel de Programación",
        help_text="El archivo debe contener las columnas ASIGNATURA, GRUPO, DIA, H.INI, H.FIN, DOCENTE",
        widget=forms.FileInput(attrs={
            'accept': '.xlsx, .xls',
            'class': 'form-control'
        })
    )

    def clean_archivo(self):
        file = self.cleaned_data['archivo']
        if not file.name.endswith('.xlsx'):
            raise forms.ValidationError("El archivo debe tener extensión .xlsx")
        return file
