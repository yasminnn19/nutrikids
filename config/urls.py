from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Páginas principais
    path('', views.index, name='index'),
    
    # Autenticação
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Perfil do usuário
    path('perfil/', views.perfil, name='perfil'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    
    # Receitas
    path('receitas/', views.receita_list, name='receita_list'),
    path('receitas/criar/', views.criar_receita, name='criar_receita'),
    path('receitas/<int:id>/', views.receita_detail, name='receita_detail'),
    
    # Fórum
    path('forum/', views.forum, name='forum'),
    path('forum/topico/<int:id>/', views.topico_detail, name='topico_detail'),
    path('forum/criar-topico/', views.criar_topico, name='criar_topico'),
    
    # Alergias
    path('minhas-alergias/', views.minhas_alergias, name='minhas_alergias'),
    path('add-alergia/', views.add_alergia_usuario, name='add_alergia_usuario'),
    path('remove-alergia/<int:alergia_id>/', views.remove_alergia_usuario, name='remove_alergia_usuario'),
    
    # Favoritos
    path('favoritos/', views.favoritos_list, name='favoritos_list'),
    path('add-favorito/<int:receita_id>/', views.add_favorito, name='add_favorito'),
    path('remove-favorito/<int:favorito_id>/', views.remove_favorito, name='remove_favorito'),
    
    # =========================================================================
    # NOVAS URLs PARA PÁGINAS REACT (sem duplicação de mensagens)
    # =========================================================================
    path('app/', views.react_app, name='react_app'),
    path('receitas-react/', views.react_receitas, name='react_receitas'),
    path('forum-react/', views.react_forum, name='react_forum'),
    path('favoritos-react/', views.react_favoritos, name='react_favoritos'),
    path('perfil-react/', views.react_perfil, name='react_perfil'),
    path('alergias-react/', views.react_alergias, name='react_alergias'),
]

# Serve arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)