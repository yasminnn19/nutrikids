from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from .forms import ReceitaForm  # Vamos criar este formulário
import json

def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def receita_list(request):
    receitas = Receita.objects.all()
    categorias = CategoriaReceita.objects.all()
    return render(request, 'receita/list.html', {
        'receitas': receitas,
        'categorias': categorias 
    })

@login_required
def receita_detail(request, id):
    receita = get_object_or_404(Receita, idreceita=id)
    ingredientes = ReceitaHasIngrediente.objects.filter(receita=receita)
    return render(request, 'receita/detail.html', {
        'receita': receita,
        'ingredientes': ingredientes
    })

@login_required
def forum_list(request):
    forums = Forum.objects.all()
    return render(request, 'forum/list.html', {'forums': forums})

@login_required
def forum_detail(request, id):
    forum = get_object_or_404(Forum, idforum=id)
    topicos = Topico.objects.filter(forum=forum)
    return render(request, 'forum/detail.html', {
        'forum': forum,
        'topicos': topicos
    })

@login_required
def topico_detail(request, id):
    topico = get_object_or_404(Topico, idtopico=id)
    postagens = Postagem.objects.filter(topico=topico)
    return render(request, 'topico/detail.html', {
        'topico': topico,
        'postagens': postagens
    })

@login_required
@require_http_methods(["POST"])
def add_postagem(request, topico_id):
    topico = get_object_or_404(Topico, idtopico=topico_id)
    texto = request.POST.get('texto')
    
    if texto:
        postagem = Postagem.objects.create(
            texto=texto,
            usuario=request.user,
            topico=topico
        )
        return redirect('topico_detail', id=topico_id)
    
    return redirect('topico_detail', id=topico_id)

@login_required
def favoritos_list(request):
    favoritos = Favorito.objects.filter(usuario=request.user)
    return render(request, 'favoritos/list.html', {'favoritos': favoritos})

@login_required
@require_http_methods(["POST"])
def toggle_favorito(request, receita_id):
    receita = get_object_or_404(Receita, idreceita=receita_id)
    favorito, created = Favorito.objects.get_or_create(
        usuario=request.user,
        receita=receita
    )
    
    if not created:
        favorito.delete()
        return JsonResponse({'status': 'removed'})
    
    return JsonResponse({'status': 'added'})

@login_required
def minhas_alergias(request):
    alergias_usuario = AlergiaHasUsuario.objects.filter(usuario=request.user)
    alergias = Alergia.objects.all()
    return render(request, 'alergias/list.html', {
        'alergias_usuario': alergias_usuario,
        'todas_alergias': alergias
    })

@login_required
@require_http_methods(["POST"])
def add_alergia_usuario(request):
    alergia_id = request.POST.get('alergia_id')
    alergia = get_object_or_404(Alergia, idalergia=alergia_id)
    
    AlergiaHasUsuario.objects.get_or_create(
        usuario=request.user,
        alergia=alergia
    )
    
    return redirect('minhas_alergias')

@login_required
@require_http_methods(["POST"])
def remove_alergia_usuario(request, alergia_id):
    alergia_usuario = get_object_or_404(
        AlergiaHasUsuario, 
        idusuario_alergia=alergia_id,
        usuario=request.user
    )
    alergia_usuario.delete()
    
    return redirect('minhas_alergias')

@login_required
@require_http_methods(["POST"])
def criar_receita(request):
    if request.method == 'POST':
        form = ReceitaForm(request.POST, request.FILES)
        if form.is_valid():
            receita = form.save(commit=False)
            receita.usuario = request.user  # Se você tiver um campo de usuário na receita
            receita.save()
            return JsonResponse({'success': True, 'message': 'Receita criada com sucesso!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Método não permitido'})