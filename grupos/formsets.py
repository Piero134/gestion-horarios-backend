from django import forms
from datetime import datetime
from django.core.exceptions import ValidationError

class BaseHorarioFormSet(forms.BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return

        horarios_ingresados = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            if not form.cleaned_data:
                continue
            horarios_ingresados.append(form.cleaned_data)

        if not horarios_ingresados:
            return

        grupo = self.instance
        if not grupo.asignatura:
            return

        asignatura = grupo.asignatura

        requerido = {
            'T': float(asignatura.horas_teoria),
            'P': float(asignatura.horas_practica),
            'L': float(asignatura.horas_laboratorio),
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

        errores_encontrados = []
        for tipo, horas_req in requerido.items():
            horas_usuario = round(acumulado[tipo], 2) # Redondear para evitar 3.000004

            # Si hay discrepancia, preparamos el mensaje de error
            if horas_usuario != horas_req:
                if horas_req > 0 or horas_usuario > 0: # Solo avisar si se requieren o se pusieron horas
                    errores_encontrados.append(
                        f"{tipo}: Se requieren {horas_req}h, ingresaste {horas_usuario}h."
                    )

        if errores_encontrados:
            raise ValidationError(
                "Error en la carga horaria: " + " | ".join(errores_encontrados)
            )

class BaseDistribucionVacantesFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        # Inyectar el usuario en cada form individual
        kwargs['user'] = self.user
        return super()._construct_form(i, **kwargs)
