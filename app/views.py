from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from .forms import ReceitaForm
import json
from django.utils import timezone
from django.db import models as django_models
from django.contrib.auth import logout

def custom_logout(request):
    logout(request)
    return redirect('index')

from django.http import JsonResponse

@login_required
def favoritos_list(request):
    """Página para listar receitas favoritas do usuário"""
    favoritos = Favorito.objects.filter(usuario=request.user).select_related('receita')
    return render(request, 'favoritos/list.html', {
        'favoritos': favoritos
    })

@login_required
@require_http_methods(["POST"])
def add_favorito(request, receita_id):
    """Adicionar receita aos favoritos"""
    receita = get_object_or_404(Receita, idreceita=receita_id)
    
    # Verificar se já é favorito
    favorito, created = Favorito.objects.get_or_create(
        usuario=request.user,
        receita=receita
    )
    
    if created:
        messages.success(request, 'Receita adicionada aos favoritos!')
    else:
        messages.info(request, 'Esta receita já está nos seus favoritos.')
    
    return redirect('receita_list')

@login_required
@require_http_methods(["POST"])
def remove_favorito(request, favorito_id):
    """Remover receita dos favoritos"""
    favorito = get_object_or_404(Favorito, idfavorito=favorito_id, usuario=request.user)
    favorito.delete()
    messages.success(request, 'Receita removida dos favoritos.')
    return redirect('favoritos_list')

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


def cadastro(request):
    if request.method == 'POST':
        # Receber dados do formulário
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        alergias_selecionadas = request.POST.getlist('alergias')  # Alergias selecionadas
        
        # Validações básicas
        if password1 != password2:
            return render(request, 'cadastro.html', {
                'error': 'As senhas não coincidem.',
                'todas_alergias': Alergia.objects.all()
            })
        
        if Usuario.objects.filter(email=email).exists():
            return render(request, 'cadastro.html', {
                'error': 'Este email já está cadastrado.',
                'todas_alergias': Alergia.objects.all()
            })
        
        # Criar usuário
        try:
            user = Usuario.objects.create_user(
                email=email,
                nome=nome,
                password=password1,
                perfil='usuario'  # Perfil padrão
            )
            
            # Adicionar alergias selecionadas
            for alergia_id in alergias_selecionadas:
                alergia = Alergia.objects.get(idalergia=alergia_id)
                AlergiaHasUsuario.objects.create(usuario=user, alergia=alergia)
            
            # Login automático após cadastro
            login(request, user)
            return redirect('index')
            
        except Exception as e:
            return render(request, 'cadastro.html', {
                'error': 'Erro ao criar conta. Tente novamente.',
                'todas_alergias': Alergia.objects.all()
            })
    
    else:
        # GET request - mostrar formulário
        return render(request, 'cadastro.html', {
            'todas_alergias': Alergia.objects.all()
        })


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

@login_required
def criar_topico(request):
    if request.method == 'POST':
        print("DEBUG: Iniciando criação de receita...")
        
        # Dados da receita
        titulo = request.POST.get('titulo')
        categorias_ids = request.POST.getlist('categorias')
        ingredientes = request.POST.get('ingredientes')
        modo_preparo = request.POST.get('modo_preparo')
        tempo_preparo = request.POST.get('tempo_preparo')
        porcoes = request.POST.get('porcoes')
        imagem = request.FILES.get('imagem')
        
        print(f"DEBUG: Titulo: {titulo}")
        print(f"DEBUG: Categorias: {categorias_ids}")
        print(f"DEBUG: Tempo: {tempo_preparo}, Porções: {porcoes}")
        
        if titulo and categorias_ids and ingredientes and modo_preparo:
            try:
                # Converter IDs para inteiros
                categorias_ids = [int(cat_id) for cat_id in categorias_ids]
                
                # Criar a receita
                receita = Receita.objects.create(
                    titulo=titulo,
                    ingredientes=ingredientes,
                    modo_preparo=modo_preparo,
                    tempo_preparo=tempo_preparo or 0,
                    porcoes=porcoes or 1,
                    imagem=imagem
                )
                
                # Adicionar as categorias selecionadas
                categorias = CategoriaReceita.objects.filter(idcategoria_receita__in=categorias_ids)
                receita.categorias_receita.set(categorias)
                
                print(f"DEBUG: Receita criada com ID: {receita.idreceita}")
                messages.success(request, 'Receita criada com sucesso!')
                return redirect('receita_detail', id=receita.idreceita)
                
            except Exception as e:
                print(f"ERRO ao criar receita: {str(e)}")
                import traceback
                traceback.print_exc()  # ← Isso mostra o traceback completo
                messages.error(request, f'Erro ao criar receita: {str(e)}')
                return redirect('forum')
        else:
            print("DEBUG: Campos obrigatórios faltando")
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return redirect('forum')
    
    # Se for GET, redireciona para o fórum
    return redirect('forum')

@login_required
def editar_perfil(request):
    usuario = request.user
    todas_alergias = Alergia.objects.all()
    alergias_usuario = AlergiaHasUsuario.objects.filter(usuario=usuario)
    
    if request.method == 'POST':
        # Atualizar informações básicas
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        
        if nome:
            usuario.nome = nome
        
        # Verificar se email já existe (exceto para o próprio usuário)
        if email and email != usuario.email:
            if Usuario.objects.filter(email=email).exclude(idusuario=usuario.idusuario).exists():
                messages.error(request, 'Este email já está em uso por outro usuário.')
                return redirect('perfil')  # Redireciona para o perfil com mensagem de erro
            else:
                usuario.email = email
        
        # Atualizar alergias
        alergias_selecionadas = request.POST.getlist('alergias')
        
        # Remover alergias existentes
        alergias_usuario.delete()
        
        # Adicionar novas alergias selecionadas
        for alergia_id in alergias_selecionadas:
            alergia = Alergia.objects.get(idalergia=alergia_id)
            AlergiaHasUsuario.objects.create(usuario=usuario, alergia=alergia)
        
        usuario.save()
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('perfil')  # Redireciona para o perfil com mensagem de sucesso
    
    context = {
        'usuario': usuario,
        'todas_alergias': todas_alergias,
        'alergias_usuario': alergias_usuario,
    }
    return render(request, 'editar_perfil.html', context)

# Atualize a view forum para incluir paginação
def forum(request):
    # Buscar todos os tópicos de forma simples
    topicos = Topico.objects.all().order_by('-idtopico')
    
    # Buscar categorias
    categorias = Categoria.objects.all()
    
    context = {
        'topicos': topicos,
        'categorias': categorias,
    }
    return render(request, 'forum.html', context)
def index(request):
    receitas = Receita.objects.all().order_by('-idreceita')[:6]
    
    # receitas = Receita.objects.all().order_by('?')[:6] --> aleatórias
    
    return render(request, 'index.html', {
        'receitas': receitas
    })


def login_view(request):
    if request.method == 'POST':
        # CORREÇÃO: Usar request.POST diretamente
        email = request.POST.get('username')  # O campo se chama 'username' no form
        password = request.POST.get('password')
        
        # CORREÇÃO: Autenticar usando o email como username
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            # Adicionar mensagem de erro
            return render(request, 'login.html', {
                'error': 'Email ou senha incorretos. Tente novamente.'
            })
    else:
        return render(request, 'login.html')


@login_required
def minhas_alergias(request):
    alergias_usuario = AlergiaHasUsuario.objects.filter(usuario=request.user)
    alergias = Alergia.objects.all()
    return render(request, 'alergias/list.html', {
        'alergias_usuario': alergias_usuario,
        'todas_alergias': alergias
    })


@login_required
def perfil(request):
    # Buscar alergias do usuário
    alergias_usuario = AlergiaHasUsuario.objects.filter(usuario=request.user)
    
    # Contexto com dados do usuário
    context = {
        'user': request.user,
        'alergias_usuario': alergias_usuario,
        'active_tab': 'perfil'
    }
    return render(request, 'perfil.html', context)


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
def receita_detail(request, id):
    receita = get_object_or_404(Receita, idreceita=id)
    ingredientes = ReceitaHasIngrediente.objects.filter(receita=receita)
    return render(request, 'receita/detail.html', {
        'receita': receita,
        'ingredientes': ingredientes
    })


@login_required
def receita_list(request):
    receitas = Receita.objects.all()
    categorias = CategoriaReceita.objects.all()
    
    # Filtro por busca
    busca = request.GET.get('busca')
    if busca:
        receitas = receitas.filter(titulo__icontains=busca)
    
    return render(request, 'receita/list.html', {
        'receitas': receitas,
        'categorias': categorias,
        'termo_busca': busca  # Para mostrar o que foi buscado
    })


@login_required
def topico_detail(request, id):
    topico = get_object_or_404(Topico, idtopico=id)
    postagens = Postagem.objects.filter(topico=topico).select_related('usuario').order_by('data_publicacao')
    
    if request.method == 'POST':
        texto = request.POST.get('texto')
        if texto and texto.strip():
            # Criar a postagem (comentário)
            Postagem.objects.create(
                texto=texto.strip(),
                usuario=request.user,
                topico=topico
            )
            messages.success(request, 'Comentário publicado com sucesso!')
            return redirect('topico_detail', id=id)
        else:
            messages.error(request, 'O comentário não pode estar vazio.')
    
    context = {
        'topico': topico,
        'postagens': postagens
    }
    return render(request, 'topico/detail.html', context)