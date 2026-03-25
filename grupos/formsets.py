from django import forms
from datetime import datetime
from django.core.exceptions import ValidationError


class BaseHorarioFormSet(forms.BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['user'] = self.user
        return kwargs


    def clean(self):
        super().clean()

        if any(self.errors):
            return

        horarios_validos = []
        acumulado = {'T': 0.0, 'P': 0.0, 'L': 0.0}
        dummy_date = datetime.today()

        for form in self.forms:
            # Ignorar formularios vacíos o marcados para eliminación
            if not form.cleaned_data or (self.can_delete and self._should_delete_form(form)):
                continue

            tipo = form.cleaned_data.get('tipo')
            inicio = form.cleaned_data.get('hora_inicio')
            fin = form.cleaned_data.get('hora_fin')
            dia = form.cleaned_data.get('dia')

            if all([tipo, inicio, fin, dia]):
                horarios_validos.append(form.cleaned_data)

                # Sumar horas
                dt_inicio = datetime.combine(dummy_date, inicio)
                dt_fin = datetime.combine(dummy_date, fin)
                acumulado[tipo] += (dt_fin - dt_inicio).total_seconds() / 3600

        if not horarios_validos:
            raise ValidationError("El grupo debe tener al menos un horario registrado.")

        grupo = self.instance
        if not grupo or not getattr(grupo, 'asignatura_base_id', None):
            return

        asignatura = grupo.asignatura_base

        requerido = {
            'T': float(asignatura.horas_teoria or 0),
            'P': float(asignatura.horas_practica or 0),
            'L': float(asignatura.horas_laboratorio or 0),
        }

        errores_horas = []

        for tipo, horas_req in requerido.items():
            horas_usuario = round(acumulado[tipo], 2)
            # Validamos si hay diferencia (permite un margen de error de redondeo)
            if abs(horas_req - horas_usuario) > 0.01:
                # Solo reportamos si la asignatura pide horas de este tipo, o si el usuario puso horas de más
                if horas_req > 0 or horas_usuario > 0:
                    errores_horas.append(f"{tipo}: Requiere {horas_req}h, ingresaste {horas_usuario}h.")

        if errores_horas:
            # Generamos un solo error global para el Formset
            raise ValidationError(
                "La carga horaria no coincide con la asignatura: " + " | ".join(errores_horas)
            )

        # Validar cruces internos entre horarios del mismo formset
        for i in range(len(horarios_validos)):
            h1 = horarios_validos[i]
            for j in range(i + 1, len(horarios_validos)):
                h2 = horarios_validos[j]

                mismo_dia = h1['dia'] == h2['dia']
                if mismo_dia:
                    # Lógica de solapamiento de tiempo
                    if h1['hora_inicio'] < h2['hora_fin'] and h1['hora_fin'] > h2['hora_inicio']:
                        raise ValidationError(
                            f"Existe un cruce de horarios el día {h1['dia']}: "
                            f"({h1['hora_inicio'].strftime('%H:%M')} - {h1['hora_fin'].strftime('%H:%M')}) con "
                            f"({h2['hora_inicio'].strftime('%H:%M')} - {h2['hora_fin'].strftime('%H:%M')})."
                        )


class BaseGrupoAsignaturaFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['user'] = self.user
        return kwargs

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        grupo = self.instance
        asignatura_base = getattr(grupo, 'asignatura_base', None)
        asignaturas_vistas = set()

        for form in self.forms:
            if not form.cleaned_data:
                continue

            asignatura = form.cleaned_data.get('asignatura')

            if self.can_delete and self._should_delete_form(form):
                # Prevenir que borren la asignatura base del grupo
                if asignatura and asignatura_base and asignatura == asignatura_base:
                    raise ValidationError(
                        f"No se puede eliminar la asignatura base del grupo ({asignatura_base.nombre})."
                    )
                continue

            if asignatura:
                if asignatura in asignaturas_vistas:
                    form.add_error('asignatura', 'Esta asignatura ya fue agregada a este grupo.')
                else:
                    asignaturas_vistas.add(asignatura)
