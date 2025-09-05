# config/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', index, name='index'),
    path('receita/', receita_list, name='receita_list'),
    path('receita/<int:id>/', receita_detail, name='receita_detail'),
    path('receita/criar/', criar_receita, name='criar_receita'),  # NOVA URL
    path('forum/', forum_list, name='forum_list'),
    path('forum/<int:id>/', forum_detail, name='forum_detail'),
    path('topico/<int:id>/', topico_detail, name='topico_detail'),
    path('topico/<int:topico_id>/postagem/', add_postagem, name='add_postagem'),
    path('favoritos/', favoritos_list, name='favoritos_list'),
    path('favoritos/toggle/<int:receita_id>/', toggle_favorito, name='toggle_favorito'),
    path('alergias/', minhas_alergias, name='minhas_alergias'),
    path('alergias/add/', add_alergia_usuario, name='add_alergia_usuario'),
    path('alergias/remove/<int:alergia_id>/', remove_alergia_usuario, name='remove_alergia_usuario'),
]

# Adicione esta linha para servir arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)