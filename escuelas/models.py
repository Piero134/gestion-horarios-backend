from django.db import models
from facultades.models import Facultad

class EscuelaQuerySet(models.QuerySet):
    def para_usuario(self, user):
        rol_name = getattr(user.rol, 'name', None) if hasattr(user, 'rol') and user.rol else None

        if rol_name == 'Vicedecano Académico' and hasattr(user, 'facultad'):
            return self.filter(facultad=user.facultad)

        if rol_name in ['Coordinador de Estudios Generales', 'Jefe de Estudios Generales'] and hasattr(user, 'facultad'):
            # Lógica de escuela principal (ordenada por código)
            escuela_principal = self.filter(facultad=user.facultad).order_by('codigo').first()
            if escuela_principal:
                return self.filter(pk=escuela_principal.pk)
            return self.none()

        if hasattr(user, 'escuela') and user.escuela:
            return self.filter(id=user.escuela.id)

        return self.none()

class EscuelaManager(models.Manager):
    def get_queryset(self):
        return EscuelaQuerySet(self.model, using=self._db)

    def para_usuario(self, user):
        return self.get_queryset().para_usuario(user)

class Escuela(models.Model):
    facultad = models.ForeignKey(
        Facultad,
        on_delete=models.PROTECT,
        related_name='escuelas'
    )
    nombre = models.CharField(max_length=150, unique=True)
    codigo = models.CharField(max_length=50, editable=False, unique=True)

    objects = EscuelaManager()

    class Meta:
        verbose_name = "Escuela Profesional"
        verbose_name_plural = "Escuelas Profesionales"
        ordering = ('codigo',)

    def save(self, *args, **kwargs):
        # Solo generar el código si es nueva
        if not self.pk:
            ultimo = (
                Escuela.objects
                .filter(facultad=self.facultad)
                .order_by('-codigo')
                .first()
            )

            if ultimo:
                ultimo_num = int(ultimo.codigo.split('.')[-1])
                siguiente = ultimo_num + 1
            else:
                siguiente = 1

            self.codigo = f"{self.facultad.codigo}.{siguiente}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
