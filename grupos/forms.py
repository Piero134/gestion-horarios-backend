import datetime
from django import forms
from django.forms import inlineformset_factory
from grupos.models import Grupo, DistribucionVacantes
from horarios.models import Horario
from asignaturas.models import Asignatura
from docentes.models import Docente
from escuelas.models import Escuela
from aulas.models import Aula
from .formsets import BaseHorarioFormSet, BaseDistribucionVacantesFormSet

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
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        aulas_qs = Aula.objects.filter(activo=True)
        docentes_qs = Docente.objects.filter(activo=True)

        if user :
            facultad_user = user.facultad
            aulas_qs = aulas_qs.filter(facultad=facultad_user)
            docentes_qs = docentes_qs.filter(facultad=facultad_user)

        self.fields['aula'].queryset = aulas_qs.order_by('pabellon', 'nombre')
        self.fields['docente'].queryset = docentes_qs.order_by(
            'apellido_paterno',
            'apellido_materno',
            'nombres'
        )

        for field in self.fields:
            if self.errors.get(field):
                self.fields[field].widget.attrs['class'] += ' is-invalid'

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')

        if hora_inicio and hora_fin:
            if hora_inicio < datetime.time(8, 0) or hora_fin > datetime.time(22, 0):
                self.add_error('hora_inicio', "El horario debe estar entre 08:00 a.m. y 10:00 p.m.")

            if hora_fin <= hora_inicio:
                self.add_error('hora_fin', "La hora de fin debe ser posterior a la hora de inicio.")

        grupo = self.instance.grupo if self.instance.pk else self.initial.get('grupo')

        if grupo and hora_inicio and hora_fin:
            dia = cleaned_data.get('dia')
            docente = cleaned_data.get('docente')
            aula = cleaned_data.get('aula')
            periodo = grupo.periodo

            # Validar cruce de aula
            if aula:
                existe_cruce_aula = Horario.objects.filter(
                    grupo__periodo=periodo,
                    dia=dia,
                    aula=aula,
                    hora_inicio__lt=hora_fin,
                    hora_fin__gt=hora_inicio
                ).exclude(pk=self.instance.pk).exclude(grupo=grupo).exists()

                if existe_cruce_aula:
                    self.add_error('aula', "El aula ya está ocupada en ese horario.")

            # Validar cruce de docente
            if docente:
                existe_cruce_docente = Horario.objects.filter(
                    grupo__periodo=periodo,
                    dia=dia,
                    docente=docente,
                    hora_inicio__lt=hora_fin,
                    hora_fin__gt=hora_inicio
                ).exclude(pk=self.instance.pk).exclude(grupo=grupo).exists()

                if existe_cruce_docente:
                    self.add_error('docente', "El docente ya tiene una clase en ese horario.")

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
        fields = ['numero', 'asignatura']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': 1}),
            'asignatura': forms.Select(attrs={
                'class': 'form-select select2-asignatura',
                'data-placeholder': 'Buscar asignatura...'
            }),
        }

        labels = {
            'numero': 'Número de Grupo',
            'asignatura': 'Asignatura',
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
        if not self.user:
            self.fields['escuela_filtro'].queryset = Escuela.objects.none()

        else:
            rol = getattr(self.user, 'rol', None)
            facultad = getattr(self.user, 'facultad', None)
            escuela_usuario = getattr(self.user, 'escuela', None)

            qs_escuelas = Escuela.objects.none()

            if rol and rol.name == 'Vicedecano Académico' and facultad:
                qs_escuelas = Escuela.objects.filter(
                    facultad=facultad
                ).order_by('codigo')

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
                qs_escuelas = Escuela.objects.filter(
                    pk=escuela_usuario.pk
                )

                self.fields['escuela_filtro'].initial = escuela_usuario
                self.fields['escuela_filtro'].disabled = True

            self.fields['escuela_filtro'].queryset = qs_escuelas

        # Lógica de carga de asignatura (Select2 AJAX friendly)
        self.fields['asignatura'].queryset = Asignatura.objects.none()

        if 'asignatura' in self.data:
            try:
                asignatura_id = int(self.data.get('asignatura'))
                self.fields['asignatura'].queryset = Asignatura.objects.filter(pk=asignatura_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['asignatura'].queryset = Asignatura.objects.filter(pk=self.instance.asignatura.pk)

            # Pre-llenar filtros si estamos editando
            if 'escuela_filtro' in self.fields and not isinstance(self.fields['escuela_filtro'].widget, forms.HiddenInput):
                self.fields['escuela_filtro'].initial = self.instance.asignatura.plan.escuela
            self.fields['ciclo_filtro'].initial = self.instance.asignatura.ciclo

        if self.instance.pk:
            # Si el grupo ya existe (estamos editando):

            # Bloquear Asignatura (No se debe cambiar el curso base)
            self.fields['periodo_display'].disabled = True
            self.fields['asignatura'].disabled = True

            # Bloquear Filtros
            self.fields['escuela_filtro'].disabled = True
            self.fields['ciclo_filtro'].disabled = True


    def save(self, commit=True):
        grupo = super().save(commit=False)
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
        asignatura = cleaned_data.get('asignatura')

        if numero and asignatura and self.periodo_activo:
            existe = Grupo.objects.filter(
                numero=numero,
                asignatura=asignatura,
                periodo=self.periodo_activo
            ).exclude(pk=self.instance.pk).exists()

            if existe:
                self.add_error(
                    'numero',
                    f"Ya existe un grupo con número {numero} para esa asignatura en el período activo."
                )

class DistribucionVacantesForm(forms.ModelForm):
    """Formulario para distribución de vacantes"""
    class Meta:
        model = DistribucionVacantes
        fields = ['asignatura', 'cantidad']
        widgets = {
            'asignatura': forms.Select(attrs={'class': 'form-select select2-asignatura-equivalente vacante-asignatura'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control vacantes-input', 'min': '1'}),
        }
        labels = {
            'asignatura': 'Plan / Asignatura Equivalente',
            'cantidad': 'Vacantes'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Definir el Universo permitido según permisos
        qs_permitido = Asignatura.objects.all()
        if user:
            if hasattr(user, 'rol') and user.rol.name == 'Vicedecano Académico':
                qs_permitido = qs_permitido.filter(plan__escuela__facultad=user.facultad)
            elif hasattr(user, 'escuela') and user.escuela:
                qs_permitido = qs_permitido.filter(plan__escuela=user.escuela)

        # Inicialmente vacío para optimizar carga
        self.fields['asignatura'].queryset = Asignatura.objects.none()

        # Recuperar dato si es POST (Bound form) o GET (Edit form)
        campo_asignatura = self.add_prefix('asignatura')

        if self.data and campo_asignatura in self.data:
            try:
                asignatura_id = int(self.data.get(campo_asignatura))
                self.fields['asignatura'].queryset = qs_permitido.filter(pk=asignatura_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['asignatura'].queryset = qs_permitido.filter(pk=self.instance.asignatura.pk)

# Forset para Horarios y Vacantes

HorarioFormSet = inlineformset_factory(
    Grupo,
    Horario,
    form=HorarioForm,        # Usamos el form horario
    formset=BaseHorarioFormSet,
    extra=1,
    can_delete=True,
    validate_min=True        # Valida que se cumpla el min_num
)

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
