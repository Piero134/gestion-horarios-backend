from django import forms
from datetime import datetime
from django.core.exceptions import ValidationError


class BaseHorarioFormSet(forms.BaseInlineFormSet):

    def clean(self):
        super().clean()

        horarios_validos = []

        for form in self.forms:

            if not hasattr(form, "cleaned_data"):
                continue

            if self.can_delete and self._should_delete_form(form):
                continue

            cleaned = form.cleaned_data

            # Ignorar formularios vacíos
            if not any([
                cleaned.get('dia'),
                cleaned.get('hora_inicio'),
                cleaned.get('hora_fin'),
                cleaned.get('tipo'),
                cleaned.get('aula'),
                cleaned.get('docente'),
            ]):
                continue

            horarios_validos.append((form, cleaned))

        # Validar que exista al menos un horario válido
        if not horarios_validos:
            raise ValidationError("Debe registrar al menos un horario.")

        grupo = self.instance
        if not grupo or not getattr(grupo, 'asignatura_id', None):
            return

        asignatura = grupo.asignatura

        requerido = {
            'T': float(asignatura.horas_teoria or 0),
            'P': float(asignatura.horas_practica or 0),
            'L': float(asignatura.horas_laboratorio or 0),
        }

        acumulado = {k: 0.0 for k in requerido}
        dummy_date = datetime.today()

        # Calcular horas ingresadas
        for form, h in horarios_validos:
            tipo = h.get('tipo')
            inicio = h.get('hora_inicio')
            fin = h.get('hora_fin')

            if tipo in acumulado and inicio and fin:
                dt_inicio = datetime.combine(dummy_date, inicio)
                dt_fin = datetime.combine(dummy_date, fin)

                diff = (dt_fin - dt_inicio).total_seconds() / 3600
                acumulado[tipo] += diff

        # Validar carga horaria
        errores = []

        for tipo, horas_req in requerido.items():
            horas_usuario = round(acumulado[tipo], 2)

            if abs(horas_req - horas_usuario) > 0.01:
                if horas_req > 0 or horas_usuario > 0:
                    errores.append(
                        f"{tipo}: Requiere {horas_req}h, ingresaste {horas_usuario}h."
                    )

        if errores:
            mensaje = "La carga horaria no coincide: " + " | ".join(errores)

            for form, _ in horarios_validos:
                form.add_error(None, mensaje)

        # Validar cruces entre horarios

        for i in range(len(horarios_validos)):
            form1, h1 = horarios_validos[i]

            for j in range(i + 1, len(horarios_validos)):
                form2, h2 = horarios_validos[j]

                mismo_dia = h1.get('dia') == h2.get('dia')

                inicio1 = h1.get('hora_inicio')
                fin1 = h1.get('hora_fin')
                inicio2 = h2.get('hora_inicio')
                fin2 = h2.get('hora_fin')

                if not (inicio1 and fin1 and inicio2 and fin2):
                    continue

                cruce = inicio1 < fin2 and fin1 > inicio2

                if mismo_dia and cruce:

                    mensaje = (
                        f"El horario {inicio1.strftime('%H:%M')} - {fin1.strftime('%H:%M')} "
                        f"cruza con {inicio2.strftime('%H:%M')} - {fin2.strftime('%H:%M')}."
                    )

                    form1.add_error(None, mensaje)
                    form2.add_error(None, mensaje)

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

        if not activos:
            return

        # Validación opcional: evitar asignaturas duplicadas
        asignaturas_vistas = set()
        for form in activos:
            asignatura = form.cleaned_data.get('asignatura')
            if asignatura in asignaturas_vistas:
                raise ValidationError("No puede repetir la misma asignatura en vacantes.")
            asignaturas_vistas.add(asignatura)
