from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from datetime import datetime
from escuelas.models import Escuela

class HorarioQuerySet(models.QuerySet):
    def para_usuario(self, user):
        escuelas_permitidas = Escuela.objects.para_usuario(user)

        if not escuelas_permitidas.exists():
            return self.none()

        qs = self.filter(grupo__asignatura__plan__escuela__in=escuelas_permitidas)

        rol_name = getattr(user.rol, 'name', None) if hasattr(user, 'rol') and user.rol else None

        if rol_name in ['Coordinador de Estudios Generales', 'Jefe de Estudios Generales']:
            qs = qs.filter(grupo__asignatura__ciclo__in=[1, 2])

        return qs

class HorarioManager(models.Manager):
    def get_queryset(self):
        return HorarioQuerySet(self.model, using=self._db)

    def para_usuario(self, user):
        return self.get_queryset().para_usuario(user)

class Horario(models.Model):
    # Dias de la semana
    DIAS_CHOICES = [
        (1, 'Lunes'),
        (2, 'Martes'),
        (3, 'Miércoles'),
        (4, 'Jueves'),
        (5, 'Viernes'),
        (6, 'Sábado'),
        (7, 'Domingo'),
    ]

    TIPO_CHOICES = [
        ('T', 'Teoría'),
        ('P', 'Práctica'),
        ('L', 'Laboratorio'),
    ]

    grupo = models.ForeignKey(
        'grupos.Grupo',
        on_delete=models.CASCADE,
        related_name='horarios'
    )

    tipo = models.CharField(
        max_length=1,
        choices=TIPO_CHOICES,
        default='T',
        verbose_name="Tipo de sesión"
    )

    dia = models.PositiveSmallIntegerField(choices=DIAS_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    aula = models.ForeignKey(
        'aulas.Aula',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='horarios'
    )

    docente = models.ForeignKey(
        'docentes.Docente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='horarios_asignados' # Cambiamos el related_name
    )

    objects = HorarioManager()

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        ordering = ['dia', 'hora_inicio']

    def __str__(self):
        nombre_aula = self.aula.nombre if self.aula else "Sin Aula"
        nombre_docente = self.docente if self.docente else "Sin Docente"
        return f"{self.get_dia_display()}: {self.hora_inicio} - {self.hora_fin} ({nombre_aula}) - {nombre_docente}"

    def obtener_cruce(self, queryset):
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        return queryset.filter(
            dia=self.dia,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio
        ).first()

    def clean(self):
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")

        if not self.grupo_id:
            return

        qs_periodo = Horario.objects.filter(grupo__periodo=self.grupo.periodo)

        if self.aula:
            cruce_aula = self.obtener_cruce(qs_periodo.filter(aula=self.aula))
            if cruce_aula:
                raise ValidationError(f"El aula {self.aula} ya está ocupada en este horario.")

        if self.docente:
            cruce_docente = self.obtener_cruce(qs_periodo.filter(docente=self.docente))
            if cruce_docente:
                raise ValidationError({
                    'docente': f"El docente {self.docente} ya tiene clase en el Grupo {cruce_docente.grupo}."
                })

        asignatura = self.grupo.asignatura

        horas_requeridas = {
            'T': asignatura.horas_teoria,
            'P': asignatura.horas_practica,
            'L': asignatura.horas_laboratorio,
        }

        fecha_base = datetime.now().date()

        inicio = datetime.combine(fecha_base, self.hora_inicio)
        fin = datetime.combine(fecha_base, self.hora_fin)
        duracion_actual = (fin - inicio).seconds / 3600

        total_por_tipo = {'T': 0, 'P': 0, 'L': 0}

        # Traemos horarios excluyendo el actual
        horarios = self.grupo.horarios.all()
        if self.pk:
            horarios = horarios.exclude(pk=self.pk)

        for h in horarios:
            if not h.hora_inicio or not h.hora_fin:
                continue

            hi = datetime.combine(fecha_base, h.hora_inicio)
            hf = datetime.combine(fecha_base, h.hora_fin)

            if h.tipo in total_por_tipo:
                total_por_tipo[h.tipo] += (hf - hi).seconds / 3600

        if self.tipo in total_por_tipo:
            total_por_tipo[self.tipo] += duracion_actual

        limite = horas_requeridas.get(self.tipo, 0)

        if round(total_por_tipo[self.tipo], 2) > limite:
            raise ValidationError(
                f"Las horas de {self.get_tipo_display()} ({round(total_por_tipo[self.tipo], 2)}) "
                f"exceden lo permitido para la asignatura ({limite} horas)."
            )
