from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db import models as django_models
import json

from .models import *
from .forms import ReceitaForm

from django.contrib.auth import logout 
from django.utils import timezone
from datetime import timedelta
from .models import Receita

def index(request):
    # Receitas populares - Ordenar por ID (mais recentes primeiro)
    receitas_populares = Receita.objects.all().order_by('-idreceita')[:3]
    
    # Receitas recentes (últimas 3 receitas adicionadas)
    receitas_recentes = Receita.objects.all().order_by('-idreceita')[:3]
    
    # Últimos tópicos do fórum (3 mais recentes)
    ultimos_topicos = Topico.objects.all().select_related('categoria', 'usuario').order_by('-idtopico')[:3]
    
    context = {
        'receitas': receitas_populares,
        'receitas_recentes': receitas_recentes,
        'ultimos_topicos': ultimos_topicos,  # novo
    }
    return render(request, 'index.html', context)

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
    
    # REDIRECIONAR de volta para a página da receita
    return redirect('receita_detail', id=receita_id)
    
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
    todas_alergias = Alergia.objects.all()
    
    # Mapeamento de emojis para cada alergia
    EMOJI_MAP = {
        'glúten': '🌾',
        'trigo': '🌾',
        'leite': '🥛', 
        'lactose': '🥛',
        'camarão': '🦐',
        'frutos do mar': '🐚',
        'crustáceos': '🦐',
        'ovo': '🥚',
        'ovos': '🥚',
        'amendoim': '🥜',
        'castanha': '🌰',
        'nozes': '🌰',
        'peixe': '🐟',
        'soja': '🫘',
        'milho': '🌽'
    }
    
    # Adiciona emoji a cada alergia
    for alergia in todas_alergias:
        alergia.emoji = EMOJI_MAP.get(alergia.nome.lower(), '⚠️')
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        alergias_selecionadas = request.POST.getlist('alergias')
        
        print(f"Dados recebidos - Nome: {nome}, Email: {email}")  # Debug
        
        # Validações básicas
        if not nome or not email or not password1:
            messages.error(request, 'Todos os campos são obrigatórios.')
            return render(request, 'cadastro.html', {'todas_alergias': todas_alergias})
        
        if password1 != password2:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'cadastro.html', {'todas_alergias': todas_alergias})
        
        # Verificar se email já existe no modelo Usuario personalizado
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado.')
            return render(request, 'cadastro.html', {'todas_alergias': todas_alergias})
        
        # Criar usuário
        try:
            # Criar usuário no modelo Usuario personalizado
            user = Usuario.objects.create_user(
                email=email,
                nome=nome,
                password=password1,
                perfil='usuario'  # Definindo perfil padrão
            )
            print(f"Usuário criado com ID: {user.idusuario}")  # Debug
            
            # Adicionar alergias selecionadas
            if alergias_selecionadas:
                for alergia_id in alergias_selecionadas:
                    try:
                        alergia = Alergia.objects.get(idalergia=alergia_id)
                        AlergiaHasUsuario.objects.create(
                            usuario=user,
                            alergia=alergia
                        )
                        print(f"Alergia adicionada: {alergia.nome}")  # Debug
                    except Exception as e:
                        print(f"Erro ao adicionar alergia {alergia_id}: {e}")  # Debug
            
            # Fazer login automático
            user = authenticate(request, email=email, password=password1)
            if user is not None:
                login(request, user)
                messages.success(request, 'Cadastro realizado com sucesso!')
                print("Usuário logado com sucesso!")  # Debug
                return redirect('index')
            else:
                messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
                return redirect('login')
                
        except Exception as e:
            print(f"Erro completo ao criar cadastro: {e}")  # Debug
            messages.error(request, f'Erro ao criar cadastro: {str(e)}')
            return render(request, 'cadastro.html', {'todas_alergias': todas_alergias})
    
    return render(request, 'cadastro.html', {'todas_alergias': todas_alergias})

@login_required
def criar_receita(request):
    categorias = CategoriaReceita.objects.all()
    
    if request.method == 'POST':
        print("DEBUG: Processando criação de receita...")
        
        titulo = request.POST.get('titulo')
        categorias_ids = request.POST.getlist('categorias')
        ingredientes = request.POST.get('ingredientes')
        modo_preparo = request.POST.get('modo_preparo')
        tempo_preparo = request.POST.get('tempo_preparo')
        porcoes = request.POST.get('porcoes')
        imagem = request.FILES.get('imagem')
        dificuldade = request.POST.get('dificuldade')
        
        print(f"DEBUG: Título: {titulo}")
        print(f"DEBUG: Categorias IDs: {categorias_ids}")
        print(f"DEBUG: Dificuldade: {dificuldade}")
        
        if titulo and categorias_ids and ingredientes and modo_preparo:
            try:
                # Criar a receita (agora com usuário)
                receita = Receita.objects.create(
                    titulo=titulo,
                    ingredientes=ingredientes,
                    modo_preparo=modo_preparo,
                    tempo_preparo=int(tempo_preparo) if tempo_preparo else 0,
                    porcoes=int(porcoes) if porcoes else 1,
                    imagem=imagem,
                    dificuldade=dificuldade,
                    usuario=request.user  # ⭐⭐ ADICIONE ESTA LINHA ⭐⭐
                )
                
                # Adicionar categorias ManyToMany
                categorias_selecionadas = CategoriaReceita.objects.filter(
                    idcategoria_receita__in=[int(cat_id) for cat_id in categorias_ids]
                )
                receita.categorias_receita.set(categorias_selecionadas)
                
                print(f"DEBUG: Receita criada com ID {receita.idreceita} pelo usuário {request.user.nome}")
                
                messages.success(request, 'Receita criada com sucesso!')
                return redirect('receita_detail', id=receita.idreceita)
                
            except Exception as e:
                print(f"ERRO ao criar receita: {str(e)}")
                messages.error(request, f'Erro ao criar receita: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    return render(request, 'receita/criar_receita.html', {
        'categorias': categorias
    })

# views.py - CORRIJA esta função
@login_required
def criar_topico(request):
    if request.method == 'POST':
        print("DEBUG: Iniciando criação de tópico...")
        
        titulo = request.POST.get('titulo')
        categoria_id = request.POST.get('categoria')
        enunciado = request.POST.get('enunciado')
        
        print(f"DEBUG: Título: {titulo}")
        print(f"DEBUG: Categoria ID: {categoria_id}")
        print(f"DEBUG: Enunciado: {enunciado}")
        
        if titulo and categoria_id and enunciado:
            try:
                categoria = Categoria.objects.get(idcategoria=categoria_id)
                
                # OBTER OU CRIAR UM FORUM PADRÃO
                forum, created = Forum.objects.get_or_create(
                    idforum=1,  # ID fixo para o fórum principal
                    defaults={
                        'titulo': 'Fórum Principal NutriKids',
                        'enunciado': 'Fórum principal da comunidade NutriKids para discussões sobre alergias alimentares',
                        'data_inicio': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'usuario': request.user  # Ou outro usuário admin se preferir
                    }
                )
                
                # Criar o tópico
                topico = Topico.objects.create(
                    titulo=titulo,
                    enunciado=enunciado,
                    categoria=categoria,
                    forum=forum,  # AGORA COM FORUM ASSOCIADO
                    usuario=request.user,
                    data_inicio=timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                
                print(f"DEBUG: Tópico criado com ID: {topico.idtopico}")
                messages.success(request, 'Tópico criado com sucesso!')
                return redirect('forum')
                
            except Categoria.DoesNotExist:
                print("DEBUG: Categoria não encontrada")
                messages.error(request, 'Categoria selecionada não existe.')
                return redirect('forum')
            except Exception as e:
                print(f"ERRO ao criar tópico: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.error(request, f'Erro ao criar tópico: {str(e)}')
                return redirect('forum')
        else:
            print("DEBUG: Campos obrigatórios faltando")
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return redirect('forum')
    
    return redirect('forum')

@login_required
def editar_perfil(request):
    usuario = request.user
    todas_alergias = Alergia.objects.all()
    alergias_usuario = AlergiaHasUsuario.objects.filter(usuario=usuario)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        
        if nome:
            usuario.nome = nome
        
        if email and email != usuario.email:
            if Usuario.objects.filter(email=email).exclude(idusuario=usuario.idusuario).exists():
                messages.error(request, 'Este email já está em uso por outro usuário.')
                return redirect('perfil')
            else:
                usuario.email = email
        
        alergias_selecionadas = request.POST.getlist('alergias')
        
        # Remover alergias existentes
        alergias_usuario.delete()
        
        # Adicionar novas alergias selecionadas
        for alergia_id in alergias_selecionadas:
            alergia = Alergia.objects.get(idalergia=alergia_id)
            AlergiaHasUsuario.objects.create(usuario=usuario, alergia=alergia)
        
        usuario.save()
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('perfil')
    
    context = {
        'usuario': usuario,
        'todas_alergias': todas_alergias,
        'alergias_usuario': alergias_usuario,
    }
    return render(request, 'editar_perfil.html', context)

def forum(request):
    # Obter parâmetros da URL
    categoria_id = request.GET.get('categoria')
    busca = request.GET.get('busca')
    ordenar = request.GET.get('ordenar', 'recentes')
    
    # Iniciar com todos os tópicos
    topicos = Topico.objects.all()
    
    # Aplicar filtro de categoria
    if categoria_id:
        try:
            categoria = Categoria.objects.get(idcategoria=categoria_id)
            topicos = topicos.filter(categoria=categoria)
        except Categoria.DoesNotExist:
            pass
    
    # Aplicar filtro de busca
    if busca:
        topicos = topicos.filter(
            django_models.Q(titulo__icontains=busca) | 
            django_models.Q(enunciado__icontains=busca)
        )
    
    # Aplicar ordenação CORRIGIDA
    if ordenar == 'antigos':
        topicos = topicos.order_by('data_inicio')
    elif ordenar == 'comentados':
        topicos = topicos.annotate(
            num_respostas=django_models.Count('postagem')
        ).order_by('-num_respostas')
    else:  # recentes (padrão)
        topicos = topicos.order_by('-data_inicio')
    
    # ESTATÍSTICAS CORRIGIDAS
    total_topicos = Topico.objects.count()
    total_respostas = Postagem.objects.count()
    total_usuarios = Usuario.objects.count()
    
    categorias = Categoria.objects.all()
    
    context = {
        'topicos': topicos,
        'categorias': categorias,
        'total_topicos': total_topicos,
        'total_respostas': total_respostas,
        'total_usuarios': total_usuarios,
    }
    return render(request, 'forum.html', context)


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Agora pega por 'email'
        password = request.POST.get('password')
        
        # Autenticar usando o modelo Usuario personalizado
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo de volta, {user.nome}!')
            return redirect('index')
        else:
            messages.error(request, 'Email ou senha incorretos.')
    
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
    alergias_usuario = AlergiaHasUsuario.objects.filter(usuario=request.user)
    
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
    
    # Filtro por categoria - ADICIONE ESTA PARTE
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        receitas = receitas.filter(categorias_receita__idcategoria_receita=categoria_id)
    
    return render(request, 'receita/list.html', {
        'receitas': receitas,
        'categorias': categorias,
        'termo_busca': busca
    })

@login_required
def topico_detail(request, id):
    topico = get_object_or_404(Topico, idtopico=id)
    postagens = Postagem.objects.filter(topico=topico).select_related('usuario').order_by('data_publicacao')
    
    if request.method == 'POST':
        texto = request.POST.get('texto')
        if texto and texto.strip():
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

def custom_logout(request):
    logout(request)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('index')