from django.db import models
from django.core.exceptions import ValidationError
from asignaturas.models import Asignatura, Equivalencia
from periodos.models import PeriodoAcademico
from datetime import datetime
from django.utils import timezone
from django.db.models import Q, Subquery, OuterRef, Prefetch
from django.core.validators import MinValueValidator
from escuelas.models import Escuela
from django.db.models.signals import post_save
from django.dispatch import receiver


class GrupoQuerySet(models.QuerySet):

    def actuales(self):
        hoy = timezone.now().date()
        return self.filter(
            periodo__fecha_inicio__lte=hoy,
            periodo__fecha_fin__gte=hoy
        )

    def de_docente(self, docente_id):
        return self.filter(horarios__docente_id=docente_id).distinct()

    def buscar(self, query, escuela=None):
        if not query:
            return self

        filtros = (
            Q(horarios__docente__nombres__icontains=query) |
            Q(horarios__docente__apellido_paterno__icontains=query) |
            Q(horarios__docente__apellido_materno__icontains=query)
        )

        if escuela:
            filtros |= (
                Q(asignaturas__nombre__icontains=query,
                  asignaturas__plan__escuela=escuela) |
                Q(asignaturas__codigo__icontains=query,
                  asignaturas__plan__escuela=escuela)
            )
        else:
            filtros |= (
                Q(asignatura_base__nombre__icontains=query) |
                Q(asignatura_base__codigo__icontains=query)
            )

        return self.filter(filtros).distinct()

    def con_info_completa(self):
        return self.select_related(
            'asignatura_base',
            'asignatura_base__plan',
            'periodo'
        ).prefetch_related(
            'horarios',
            'horarios__aula',
            'horarios__docente',
            'asignaturas_cubiertas',
            'asignaturas_cubiertas__asignatura',
            'asignaturas_cubiertas__asignatura__plan',
        )

    def con_asignatura_de_escuela(self, escuela):
        return self.prefetch_related(
            Prefetch(
                'asignaturas_cubiertas',
                queryset=GrupoAsignatura.objects.filter(
                    asignatura__plan__escuela=escuela
                ).select_related(
                    'asignatura',
                    'asignatura__plan',
                    'asignatura__plan__escuela',
                ),
                to_attr='asignatura_en_escuela'
            )
        )

    def para_escuela(self, escuela, solo_primeros_ciclos=False):
        qs = self.filter(
            asignaturas__plan__escuela=escuela
        ).distinct()

        if solo_primeros_ciclos:
            qs = qs.filter(asignaturas__ciclo__in=[1, 2])

        return qs.con_asignatura_de_escuela(escuela)

    def para_usuario(self, user):
        """Filtra grupos accesibles según el rol del usuario."""
        from escuelas.models import Escuela
        escuelas = Escuela.objects.para_usuario(user)
        return self.filter(
            asignaturas__plan__escuela__in=escuelas
        ).distinct()


class GrupoManager(models.Manager):

    def get_queryset(self):
        return GrupoQuerySet(self.model, using=self._db)

    def para_escuela(self, escuela, solo_primeros_ciclos=False):
        return self.get_queryset().para_escuela(escuela, solo_primeros_ciclos)

    def actuales(self):
        return self.get_queryset().actuales()

    def de_docente(self, docente_id):
        return self.get_queryset().de_docente(docente_id)

    def buscar(self, query, escuela=None):
        return self.get_queryset().buscar(query, escuela=escuela)

    def con_info_completa(self):
        return self.get_queryset().con_info_completa()

    def para_usuario(self, user):
        return self.get_queryset().para_usuario(user)


class Grupo(models.Model):
    numero = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    asignatura_base = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='grupos_base'
    )
    periodo = models.ForeignKey(
        PeriodoAcademico,
        on_delete=models.CASCADE,
        related_name='grupos'
    )
    asignaturas = models.ManyToManyField(
        Asignatura,
        through='GrupoAsignatura',
        related_name='grupos',
        blank=True
    )

    objects = GrupoManager()

    class Meta:
        unique_together = ('numero', 'asignatura_base', 'periodo')
        verbose_name = "Grupo"
        ordering = ['periodo', 'asignatura_base', 'numero']

    def __str__(self):
        nombre = getattr(self, 'nombre_asignatura', None) or self.asignatura_base.nombre
        return f"G-{self.numero} {nombre}"

    @property
    def total_vacantes(self):
        return self.asignaturas_cubiertas.aggregate(
            total=models.Sum('vacantes')
        )['total'] or 0

    def validar_horarios(self):
        asignatura = self.asignatura_base
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

        errores = {
            tipo: f"{horas_actuales[tipo]} / {requeridas} horas"
            for tipo, requeridas in horas_requeridas.items()
            if horas_actuales[tipo] != requeridas
        }
        if errores:
            raise ValidationError({
                'horarios': (
                    "La carga horaria del grupo no está completa: "
                    + ", ".join(f"{tipo}: {msg}" for tipo, msg in errores.items())
                )
            })


class GrupoAsignatura(models.Model):
    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.CASCADE,
        related_name='asignaturas_cubiertas'
    )
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='+'
    )
    vacantes = models.PositiveIntegerField(
        default=0,
        verbose_name="Vacantes reservadas"
    )

    class Meta:
        unique_together = ('grupo', 'asignatura')
        verbose_name = "Asignatura cubierta por grupo"

    def clean(self):
        if not self.grupo_id or not self.asignatura_id:
            return

        base = self.grupo.asignatura_base

        # La asignatura base siempre es válida
        if self.asignatura == base:
            return

        # Las demás deben ser equivalentes a la base
        if not Equivalencia.objects.filter(
            asignaturas=base
        ).filter(
            asignaturas=self.asignatura
        ).exists():
            raise ValidationError(
                f"{self.asignatura} no es equivalente a {base}."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"G-{self.grupo.numero} {self.asignatura.nombre}: {self.vacantes} vacantes"

    @property
    def es_base(self):
        return self.asignatura_id == self.grupo.asignatura_base_id


@receiver(post_save, sender=Grupo)
def crear_grupo_asignatura_base(sender, instance, created, **kwargs):
    """
    Creacion de grupo asignatura base al crear un nuevo grupo. Si el grupo ya tiene asignaturas en el formset, no se crea una entrada adicional.
    """
    if created:
        GrupoAsignatura.objects.get_or_create(
            grupo=instance,
            asignatura=instance.asignatura_base,
            defaults={'vacantes': 0}
        )
