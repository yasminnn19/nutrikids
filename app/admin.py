from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'nome', 'perfil', 'is_active')
    list_filter = ('perfil', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'senha')}),
        ('Informações Pessoais', {'fields': ('nome',)}),
        ('Permissões', {'fields': ('perfil', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'senha1', 'senha2', 'perfil')}
        ),
    )
    search_fields = ('email', 'nome')
    ordering = ('email',)
    filter_horizontal = ()

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