from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'username', 'rol', 'facultad', 'escuela', 'is_staff')

    list_filter = ('rol', 'facultad', 'is_staff', 'is_superuser')

    search_fields = ('email', 'first_name', 'last_name', 'username')

    ordering = ('email',)

    fieldsets = UserAdmin.fieldsets + (
        ('Información Académica UNMSM', {
            'fields': ('rol', 'facultad', 'escuela'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Académica UNMSM', {
            'fields': ('email', 'rol', 'facultad', 'escuela'),
        }),
    )

    readonly_fields = ('username',)

    filter_horizontal = ('groups', 'user_permissions')
