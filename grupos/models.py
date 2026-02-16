from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from asignaturas.models import Asignatura, Equivalencia # Importamos Equivalencia para validar
from periodos.models import PeriodoAcademico
from datetime import datetime
from django.utils import timezone
from django.db.models import Q

class GrupoQuerySet(models.QuerySet):
    def actuales(self):
        hoy = timezone.now().date()
        return self.filter(
            periodo__fecha_inicio__lte=hoy,
            periodo__fecha_fin__gte=hoy
        )

    def de_docente(self, docente_id):
        return self.filter(horarios__docente_id=docente_id).distinct()

    def buscar(self, query):
        if not query:
            return self

        return self.filter(
            Q(asignatura__nombre__icontains=query) |
            Q(asignatura__codigo__icontains=query) |
            Q(horarios__docente__nombres__icontains=query) |
            Q(horarios__docente__apellido_paterno__icontains=query) |
            Q(horarios__docente__apellido_materno__icontains=query)
        ).distinct()

    def con_info_completa(self):
        """
        Trae datos de asignatura, periodo y pre-carga horarios y aulas.
        """
        return self.select_related(
            'asignatura',
            'periodo'
        ).prefetch_related(
            'horarios',
            'horarios__aula',
            'horarios__docente',
            'vacantes'
        )

    def para_usuario(self, user):
        if hasattr(user, 'rol') and user.rol.name == 'Vicedecano Académico':
            return self.filter(asignatura__plan__escuela__facultad=user.facultad)

        if hasattr(user, 'rol') and user.rol.name in [
            'Coordinador de Estudios Generales',
            'Jefe de Estudios Generales'
        ]:
            return self.filter(
                asignatura__plan__escuela__facultad=user.facultad,
                asignatura__ciclo__in=[1, 2]
            )

        if hasattr(user, 'escuela') and user.escuela:
            return self.filter(asignatura__plan__escuela=user.escuela)
        return self.none()

class GrupoManager(models.Manager):
    def get_queryset(self):
        return GrupoQuerySet(self.model, using=self._db)

    def para_usuario(self, user):
        return self.get_queryset().para_usuario(user)

    def actuales(self):
        return self.get_queryset().actuales()

    def de_docente(self, docente):
        return self.get_queryset().de_docente(docente)

    def buscar(self, query):
        return self.get_queryset().buscar(query)

class Grupo(models.Model):
    numero = models.PositiveSmallIntegerField()
    asignatura = models.ForeignKey(
        Asignatura, on_delete=models.CASCADE, related_name='grupos'
    )
    periodo = models.ForeignKey(
        PeriodoAcademico, on_delete=models.CASCADE, related_name='grupos'
    )

    objects = GrupoManager()

    class Meta:
        unique_together = ('numero', 'asignatura', 'periodo')
        verbose_name = "Grupo"
        ordering = ['periodo', 'asignatura', 'numero']

    def __str__(self):
        return f"({self.periodo}) G-{self.numero} {self.asignatura.nombre}"

    @property
    def total_vacantes(self):
        """Suma de todas las vacantes distribuidas entre los diferentes planes"""
        return self.vacantes.aggregate(total=models.Sum('cantidad'))['total'] or 0

    def validar_horarios(self):
        asignatura = self.asignatura

        horas_requeridas = {
            'T': asignatura.horas_teoria,
            'P': asignatura.horas_practica,
            'L': asignatura.horas_laboratorio,
        }

        horas_actuales = {'T': 0, 'P': 0, 'L': 0}

        for h in self.horarios.all():
            inicio = datetime.combine(datetime.today(), h.hora_inicio)
            fin = datetime.combine(datetime.today(), h.hora_fin)
            horas_actuales[h.tipo] += (fin - inicio).seconds / 3600

        errores = {}

        for tipo, requeridas in horas_requeridas.items():
            if horas_actuales[tipo] != requeridas:
                errores[tipo] = (
                    f"{horas_actuales[tipo]} / {requeridas} horas"
                )

        if errores:
            raise ValidationError({
                'horarios': (
                    "La carga horaria del grupo no está completa: "
                    + ", ".join(
                        f"{tipo}: {msg}" for tipo, msg in errores.items()
                    )
                )
            })

class DistribucionVacantes(models.Model):
    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.CASCADE,
        related_name='vacantes'
    )

    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE
    )

    cantidad = models.PositiveIntegerField(
        verbose_name="Cantidad de Vacantes",
        help_text="Número de cupos reservados para este plan"
    )

    matriculados = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Distribución de Vacante"
        verbose_name_plural = "Distribución de Vacantes"
        unique_together = ('grupo', 'asignatura')

    def clean(self):
        try:
            if not self.grupo_id:
                return
            base = self.grupo.asignatura
        except ObjectDoesNotExist:
            return

        if self.asignatura == base:
            return

        # Validar equivalencia
        if not Equivalencia.objects.filter(
            asignaturas=base
        ).filter(
            asignaturas=self.asignatura
        ).exists():
            raise ValidationError(
                f"{self.asignatura} no es equivalente a {base}"
            )
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.grupo} -> {self.cantidad} vacantes para {self.asignatura}"
