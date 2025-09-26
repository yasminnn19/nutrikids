# config/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),  # View personalizada
    path('', index, name='index'),
    path('cadastro/', cadastro, name='cadastro'),  # Adicionei também o cadastro
    path('receita/', receita_list, name='receita_list'),
    path('receita/<int:id>/', receita_detail, name='receita_detail'),
    path('receita/criar/', criar_receita, name='criar_receita'),
    path('forum/', forum, name='forum'),
    path('topico/<int:id>/', topico_detail, name='topico_detail'),
    path('topico/<int:topico_id>/postagem/', add_postagem, name='add_postagem'),
    path('alergias/', minhas_alergias, name='minhas_alergias'),
    path('alergias/add/', add_alergia_usuario, name='add_alergia_usuario'),
    path('alergias/remove/<int:alergia_id>/', remove_alergia_usuario, name='remove_alergia_usuario'),
    path('logout/', custom_logout, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)