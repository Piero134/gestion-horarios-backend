from django import forms
from django.forms import inlineformset_factory
from grupos.models import Grupo, DistribucionVacantes
from horarios.models import Horario
from asignaturas.models import Asignatura
from docentes.models import Docente
from escuelas.models import Escuela
from .formsets import BaseHorarioFormSet, BaseDistribucionVacantesFormSet
from horarios.forms import HorarioForm

class GrupoForm(forms.ModelForm):

    escuela_filtro = forms.ModelChoiceField(
        queryset=Escuela.objects.none(),
        required=False,
        label="Filtrar por Escuela",
        widget=forms.Select(attrs={'class': 'form-select select2-escuela', 'id': 'id_escuela_filtro'})
    )

    ciclo_filtro = forms.ChoiceField(
        choices=[('', 'Todos los ciclos')] + [(i, f'Ciclo {i}') for i in range(1, 11)],
        required=False,
        label="Filtrar por Ciclo",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_ciclo_filtro'})
    )

    periodo_display = forms.CharField(
        label="Período Académico",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-light fw-bold',
            'readonly': 'readonly',
            'tabindex': '-1'
        })
    )

    class Meta:
        model = Grupo
        fields = ['numero', 'asignatura', 'docente']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 1'}),
            'asignatura': forms.Select(attrs={
                'class': 'form-select select2-asignatura',
                'data-placeholder': 'Buscar asignatura...'
            }),
            'docente': forms.Select(attrs={
                'class': 'form-select select2-docente',
                'data-placeholder': 'Seleccione un docente...'
            }),
        }

        labels = {
            'numero': 'Número de Grupo',
            'asignatura': 'Asignatura',
            'docente': 'Docente Asignado'
        }

    def __init__(self, *args, **kwargs):
        self.periodo_activo = kwargs.pop('periodo_activo', None)
        self.user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        # Periodo academico (solo display)
        if self.instance.pk:
            self.fields['periodo_display'].initial = str(self.instance.periodo)
        elif self.periodo_activo:
            self.fields['periodo_display'].initial = str(self.periodo_activo)

        # Filtro segun rol
        if self.user:
            if hasattr(self.user, 'rol') and self.user.rol.name == 'Vicedecano Académico':
                self.fields['escuela_filtro'].queryset = Escuela.objects.filter(
                    facultad=self.user.facultad
                ).order_by('codigo')
            elif hasattr(self.user, 'escuela') and self.user.escuela:
                self.fields['escuela_filtro'].queryset = Escuela.objects.filter(
                    pk=self.user.escuela.pk
                )
                self.fields['escuela_filtro'].initial = self.user.escuela
                self.fields['escuela_filtro'].widget = forms.HiddenInput()

        self.fields['asignatura'].queryset = Asignatura.objects.none()

        if 'asignatura' in self.data:
            try:
                asignatura_id = int(self.data.get('asignatura'))
                self.fields['asignatura'].queryset = Asignatura.objects.filter(pk=asignatura_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['asignatura'].queryset = Asignatura.objects.filter(pk=self.instance.asignatura.pk)

            if 'escuela_filtro' in self.fields and not isinstance(self.fields['escuela_filtro'].widget, forms.HiddenInput):
                self.fields['escuela_filtro'].initial = self.instance.asignatura.plan.escuela
            self.fields['ciclo_filtro'].initial = self.instance.asignatura.ciclo

        self.fields['docente'].queryset = Docente.objects.all().order_by('apellido', 'nombre')

    def save(self, commit=True):
        grupo = super().save(commit=False)

        if not grupo.pk and self.periodo_activo:
            grupo.periodo = self.periodo_activo

        if commit:
            grupo.save()
        return grupo

class DistribucionVacantesForm(forms.ModelForm):
    """Formulario para distribución de vacantes"""

    class Meta:
        model = DistribucionVacantes
        fields = ['asignatura', 'cantidad']
        widgets = {
            'asignatura': forms.Select(attrs={
                'class': 'vacante-asignatura'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control vacantes-input',
                'min': '1',
            }),
        }
        labels = {
            'asignatura': 'Asignatura',
            'cantidad': 'Vacantes'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Asignaturas permitidas según rol
        qs_permitido = Asignatura.objects.all()
        if user:
            if hasattr(user, 'rol') and user.rol.name == 'Vicedecano Académico':
                qs_permitido = qs_permitido.filter(plan__escuela__facultad=user.facultad)
            elif hasattr(user, 'escuela') and user.escuela:
                qs_permitido = qs_permitido.filter(plan__escuela=user.escuela)

        # Inicialmente vacío
        self.fields['asignatura'].queryset = Asignatura.objects.none()

        # Obtenenemos el campo
        campo_asignatura = self.add_prefix('asignatura')

        if self.data and campo_asignatura in self.data:
            try:
                asignatura_id = int(self.data.get(campo_asignatura))

                # Filtramos según el queryset permitido
                self.fields['asignatura'].queryset = qs_permitido.filter(pk=asignatura_id)
            except (ValueError, TypeError):
                pass

        elif self.instance.pk:
            self.fields['asignatura'].queryset = qs_permitido.filter(pk=self.instance.asignatura.pk)


HorarioFormSet = inlineformset_factory(
    Grupo,
    Horario,
    form=HorarioForm,
    formset=BaseHorarioFormSet,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)


# Formset para distribución de vacantes
DistribucionVacantesFormSet = inlineformset_factory(
    Grupo,
    DistribucionVacantes,
    formset=BaseDistribucionVacantesFormSet,
    form=DistribucionVacantesForm,
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True
)
