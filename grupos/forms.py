import datetime
from django import forms
from django.forms import inlineformset_factory
from grupos.models import Grupo, GrupoAsignatura
from horarios.models import Horario
from asignaturas.models import Asignatura
from docentes.models import Docente
from escuelas.models import Escuela
from aulas.models import Aula
from .formsets import BaseHorarioFormSet, BaseGrupoAsignaturaFormSet

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['dia', 'hora_inicio', 'hora_fin', 'tipo', 'aula', 'docente']
        widgets = {
            'dia': forms.Select(attrs={'class': 'form-select'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'aula': forms.Select(attrs={'class': 'form-select select2-aula'}),
            'docente': forms.Select(attrs={
                'class': 'form-select select2-docente',
                'data-placeholder': 'Seleccione docente'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        aulas_qs = Aula.objects.filter(activo=True).order_by('pabellon', 'nombre')
        docentes_qs = Docente.objects.filter(activo=True).order_by(
            'apellido_paterno', 'apellido_materno', 'nombres'
        )

        if self.user:
            facultad = getattr(self.user, 'facultad', None)
            if facultad:
                aulas_qs = aulas_qs.filter(facultad=facultad)
                docentes_qs = docentes_qs.filter(facultad=facultad)

        self.fields['aula'].queryset = aulas_qs
        self.fields['docente'].queryset = docentes_qs


    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')

        if hora_inicio and hora_fin:
            if hora_inicio < datetime.time(8, 0) or hora_fin > datetime.time(22, 0):
                self.add_error('hora_inicio', "El horario debe estar entre 08:00 y 22:00.")
            if hora_fin <= hora_inicio:
                self.add_error('hora_fin', "La hora de fin debe ser posterior a la de inicio.")

        return cleaned_data

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
        fields = ['numero', 'asignatura_base']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': 1}),
            'asignatura_base': forms.Select(attrs={
                'class': 'form-select select2-asignatura',
                'data-placeholder': 'Buscar asignatura...'
            }),
        }

        labels = {
            'numero': 'Número de Grupo',
            'asignatura_base': 'Asignatura',
        }

    def __init__(self, *args, **kwargs):
        self.periodo_activo = kwargs.pop('periodo_activo', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Periodo display (solo lectura)
        if self.instance.pk:
            self.fields['periodo_display'].initial = str(self.instance.periodo)
        elif self.periodo_activo:
            self.fields['periodo_display'].initial = str(self.periodo_activo)

        # Escuelas según rol
        qs_escuelas = Escuela.objects.none()
        if self.user:
            rol = getattr(self.user, 'rol', None)
            facultad = getattr(self.user, 'facultad', None)
            escuela_usuario = getattr(self.user, 'escuela', None)

            if rol and rol.name == 'Vicedecano Académico' and facultad:
                qs_escuelas = Escuela.objects.filter(facultad=facultad).order_by('codigo')

            elif rol and rol.name in [
                'Coordinador de Estudios Generales',
                'Jefe de Estudios Generales'
            ] and facultad:
                escuela_principal = (
                    Escuela.objects
                    .filter(facultad=facultad)
                    .order_by('codigo')
                    .first()
                )
                if escuela_principal:
                    qs_escuelas = Escuela.objects.filter(pk=escuela_principal.pk)
                    self.fields['escuela_filtro'].initial = escuela_principal
                    self.fields['escuela_filtro'].disabled = True

            elif escuela_usuario:
                qs_escuelas = Escuela.objects.filter(pk=escuela_usuario.pk)
                self.fields['escuela_filtro'].initial = escuela_usuario
                self.fields['escuela_filtro'].disabled = True

        self.fields['escuela_filtro'].queryset = qs_escuelas

        self.fields['asignatura_base'].queryset = Asignatura.objects.none()

        if 'asignatura_base' in self.data:
            try:
                asignatura_id = int(self.data['asignatura_base'])
                self.fields['asignatura_base'].queryset = Asignatura.objects.filter(
                    pk=asignatura_id
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['asignatura_base'].queryset = Asignatura.objects.filter(
                pk=self.instance.asignatura_base_id
            )
            # Pre-seleccionar filtros en edición
            if not self.fields['escuela_filtro'].disabled:
                self.fields['escuela_filtro'].initial = (
                    self.instance.asignatura_base.plan.escuela
                )
            self.fields['ciclo_filtro'].initial = self.instance.asignatura_base.ciclo

        # En edición, bloquear campos inmutables
        if self.instance.pk:
            for field in ('periodo_display', 'asignatura_base', 'escuela_filtro', 'ciclo_filtro'):
                self.fields[field].disabled = True

    def save(self, commit=True):
        grupo = super().save(commit=False)
        # Asignar periodo solo en creación
        if not grupo.pk and self.periodo_activo:
            grupo.periodo = self.periodo_activo
        if commit:
            grupo.save()
        return grupo

    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if numero is not None and numero < 1:
            raise forms.ValidationError("El número de grupo debe ser mayor o igual a 1.")
        return numero

    def clean(self):
        cleaned_data = super().clean()
        numero = cleaned_data.get('numero')
        asignatura_base = cleaned_data.get('asignatura_base')

        if numero and asignatura_base and self.periodo_activo:
            existe = Grupo.objects.filter(
                numero=numero,
                asignatura_base=asignatura_base,
                periodo=self.periodo_activo
            ).exclude(pk=self.instance.pk if self.instance.pk else None).exists()

            if existe:
                self.add_error(
                    'numero',
                    f"Ya existe un grupo {numero} para esa asignatura en el período activo."
                )

        return cleaned_data

class GrupoAsignaturaForm(forms.ModelForm):
    class Meta:
        model = GrupoAsignatura
        fields = ['asignatura', 'vacantes']
        widgets = {
            'asignatura': forms.Select(attrs={
                'class': 'form-select select2-asignatura-equivalente vacante-asignatura'
            }),
            'vacantes': forms.NumberInput(attrs={
                'class': 'form-control vacantes-input',
                'min': '0'
            }),
        }
        labels = {
            'asignatura': 'Plan / Asignatura',
            'vacantes': 'Vacantes',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self._setup_asignatura_queryset()

    def _setup_asignatura_queryset(self):
        qs_permitido = self._get_qs_permitido()

        # Siempre arrancamos con none; el queryset real se inyecta
        # sólo con el id que llega en POST o con el que ya tiene la instancia.
        self.fields['asignatura'].queryset = Asignatura.objects.none()

        campo_asignatura = self.add_prefix('asignatura')

        if self.data and campo_asignatura in self.data:
            try:
                asignatura_id = int(self.data[campo_asignatura])
                self.fields['asignatura'].queryset = qs_permitido.filter(
                    pk=asignatura_id
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['asignatura'].queryset = qs_permitido.filter(
                pk=self.instance.asignatura_id
            )

    def _get_qs_permitido(self):
        user = self.user
        qs = Asignatura.objects.all()

        if not user:
            return qs

        rol = getattr(user, 'rol', None)
        facultad = getattr(user, 'facultad', None)
        escuela_usuario = getattr(user, 'escuela', None)

        if rol and rol.name == 'Vicedecano Académico' and facultad:
            return qs.filter(plan__escuela__facultad=facultad)

        if rol and rol.name in [
            'Coordinador de Estudios Generales',
            'Jefe de Estudios Generales'
        ] and facultad:
            from asignaturas.models import Equivalencia
            escuela_principal = (
                Escuela.objects.filter(facultad=facultad).order_by('codigo').first()
            )
            if escuela_principal:
                asignaturas_base = Asignatura.objects.filter(
                    plan__escuela=escuela_principal,
                    ciclo__in=[1, 2]
                )
                equivalencias = Equivalencia.objects.filter(
                    asignaturas__in=asignaturas_base
                )
                return (
                    Asignatura.objects.filter(equivalencias__in=equivalencias) |
                    asignaturas_base
                ).distinct()
            return qs.none()

        if escuela_usuario:
            return qs.filter(plan__escuela=escuela_usuario)

        return qs


# Formsets

HorarioFormSet = inlineformset_factory(
    Grupo,
    Horario,
    form=HorarioForm,
    formset=BaseHorarioFormSet,
    extra=0,
    can_delete=True,
    validate_min=True,
)

GrupoAsignaturaFormSet = inlineformset_factory(
    Grupo,
    GrupoAsignatura,
    formset=BaseGrupoAsignaturaFormSet,
    form=GrupoAsignaturaForm,
    extra=0,
    can_delete=True,
    # min_num=1,  # No se requiere mínimo porque la asignatura base siempre existe
)
