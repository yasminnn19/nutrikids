from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Se você está usando o modelo Usuario personalizado, registre-o corretamente
class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'nome', 'perfil', 'is_active')
    list_filter = ('perfil', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # Mude 'senha' para 'password'
        ('Informações Pessoais', {'fields': ('nome',)}),
        ('Permissões', {'fields': ('perfil', 'is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password1', 'password2', 'perfil')}
        ),
    )
    search_fields = ('email', 'nome')
    ordering = ('email',)
    filter_horizontal = ()

# Registre apenas os modelos que existem
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Alergia)
admin.site.register(AlergiaHasUsuario)
admin.site.register(CategoriaReceita)
admin.site.register(Receita)
admin.site.register(Forum)
admin.site.register(Categoria)
admin.site.register(Topico)
admin.site.register(Postagem)
admin.site.register(Favorito)

# Verifique se PerfilUsuario existe antes de registrar
try:
    from .models import PerfilUsuario
    #admin.site.register(PerfilUsuario)
except ImportError:
    print("Modelo PerfilUsuario não encontrado - pulando registro no admin")