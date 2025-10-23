from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('receitas/', views.receita_list, name='receita_list'),
    path('receitas/criar/', views.criar_receita, name='criar_receita'),
    path('receitas/<int:id>/', views.receita_detail, name='receita_detail'),  # CORRETO: receitas (plural)
    path('forum/', views.forum, name='forum'),
    path('forum/topico/<int:id>/', views.topico_detail, name='topico_detail'),
    path('forum/criar-topico/', views.criar_topico, name='criar_topico'),
    path('minhas-alergias/', views.minhas_alergias, name='minhas_alergias'),
    path('add-alergia/', views.add_alergia_usuario, name='add_alergia_usuario'),
    path('remove-alergia/<int:alergia_id>/', views.remove_alergia_usuario, name='remove_alergia_usuario'),
    path('favoritos/', views.favoritos_list, name='favoritos_list'),
    path('add-favorito/<int:receita_id>/', views.add_favorito, name='add_favorito'),
    path('remove-favorito/<int:favorito_id>/', views.remove_favorito, name='remove_favorito'),
]