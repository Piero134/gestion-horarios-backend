<<<<<<< HEAD
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractUser):
    objects = UsuarioManager()

    email = models.EmailField('correo electrónico', unique=True)

    rol = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        verbose_name="Rol Institucional",
        help_text="Seleccione el grupo de permisos",
        null=True,
        blank=True
    )

    facultad = models.ForeignKey('facultades.Facultad', on_delete=models.PROTECT)
    escuela = models.ForeignKey(
        'escuelas.Escuela',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Seleccione la escuela a la que pertenece el usuario (si aplica)."
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['facultad_id']

    def clean(self):
        super().clean()

        if self.is_superuser:
            return

        if not self.rol:
             raise ValidationError({'rol': "El rol es obligatorio."})

        if not self.facultad:
             raise ValidationError({'facultad': "La facultad es obligatoria."})

        if self.escuela and self.escuela.facultad != self.facultad:
            raise ValidationError({
                'escuela': "La escuela seleccionada no pertenece a la facultad de este usuario."
            })

        # validar roles que requieren escuela
        if self.rol and self.rol.name in ['Secretaria de Escuela', 'Director de Escuela'] and not self.escuela:
            raise ValidationError({
                'escuela': f"El rol de {self.rol.name} requiere asignar una escuela."
            })

        # validar roles que son unicos por escuela
        if self.rol and self.rol.name in ['Secretaria de Escuela', 'Director de Escuela'] and self.escuela:
            existe = Usuario.objects.filter(rol=self.rol, escuela=self.escuela).exclude(pk=self.pk).exists()
            if existe:
                raise ValidationError(
                    f"Ya existe un usuario con el rol {self.rol.name} en la escuela de {self.escuela.nombre}."
                )

    def save(self, *args, **kwargs):
        # Username automatico basado en email
        if self.email and not self.username:
            self.username = self.email.split('@')[0]

        # Ejectutar validaciones antes de guardar
        self.full_clean()

        # Guardar objeto
        super().save(*args, **kwargs)

        # Sincronizar automáticamente con la tabla m2m de grupos de Django
        if self.rol:
            self.groups.add(self.rol)

    def __str__(self):
        rol_nombre = self.rol.name if self.rol else "Sin Rol"
        return f"{self.email} ({rol_nombre})"
=======
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
>>>>>>> 71224ecb86f8f8c385092b501f3124b34fd8718b
