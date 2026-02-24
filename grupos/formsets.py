from django import forms
from datetime import datetime
from django.core.exceptions import ValidationError

class BaseHorarioFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        horarios_ingresados = []

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            if self.can_delete and self._should_delete_form(form):
                continue

            # Ignorar formularios completamente vacíos
            if not any([
                form.cleaned_data.get('dia'),
                form.cleaned_data.get('hora_inicio'),
                form.cleaned_data.get('hora_fin'),
                form.cleaned_data.get('tipo')
            ]):
                continue

            horarios_ingresados.append(form.cleaned_data)

        if not horarios_ingresados:
            raise ValidationError("Debe registrar al menos un horario.")

        grupo = self.instance
        if not grupo.asignatura:
            return

        asignatura = grupo.asignatura

        requerido = {
            'T': float(asignatura.horas_teoria or 0),
            'P': float(asignatura.horas_practica or 0),
            'L': float(asignatura.horas_laboratorio or 0),
        }

        acumulado = {k: 0.0 for k in requerido.keys()}

        dummy = datetime.today()

        for h in horarios_ingresados:
            tipo = h.get('tipo')
            inicio = h.get('hora_inicio')
            fin = h.get('hora_fin')

            if tipo in acumulado and inicio and fin:
                dt_inicio = datetime.combine(dummy, inicio)
                dt_fin = datetime.combine(dummy, fin)

                diff_horas = (dt_fin - dt_inicio).total_seconds() / 3600
                acumulado[tipo] += diff_horas

        errores = []

        for tipo, horas_req in requerido.items():
            horas_usuario = round(acumulado[tipo], 2)

            if abs(horas_req - horas_usuario) > 0.01:
                if horas_req > 0 or horas_usuario > 0:
                    errores.append(
                        f"{tipo}: Se requieren {horas_req}h, ingresaste {horas_usuario}h."
                    )

        if errores:
            raise ValidationError(
                "La carga horaria no coincide:\n" + "\n".join(errores)
            )

class BaseDistribucionVacantesFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs['user'] = self.user
        return super()._construct_form(i, **kwargs)

    def clean(self):
        super().clean()

        activos = []

        for form in self.forms:

            if not hasattr(form, "cleaned_data"):
                continue

            if self.can_delete and self._should_delete_form(form):
                continue

            asignatura = form.cleaned_data.get('asignatura')
            cantidad = form.cleaned_data.get('cantidad')

            # Ignorar formularios totalmente vacíos
            if not asignatura and not cantidad:
                continue
            if asignatura and not cantidad:
                form.add_error('cantidad', 'Debe ingresar la cantidad.')

            if cantidad and not asignatura:
                form.add_error('asignatura', 'Debe seleccionar una asignatura.')
            activos.append(form)

        # Si quieres permitir que no haya vacantes:
        if not activos:
            return

        # Validación opcional: evitar asignaturas duplicadas
        asignaturas_vistas = set()
        for form in activos:
            asignatura = form.cleaned_data.get('asignatura')
            if asignatura in asignaturas_vistas:
                raise ValidationError("No puede repetir la misma asignatura en vacantes.")
            asignaturas_vistas.add(asignatura)
