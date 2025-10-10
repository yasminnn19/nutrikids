from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, authenticate, logout  # ADD logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages  # ADD messages
from .models import *
from .forms import ReceitaForm
import json
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index(request):

    receitas = Receita.objects.all().order_by('-idreceita')[:6]
    
    # receitas = Receita.objects.all().order_by('?')[:6] --> aleatórias
    
    return render(request, 'index.html', {
        'receitas': receitas
    })

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
    
# views.py - CORRIGIR a view login_view
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
def receita_detail(request, id):
    receita = get_object_or_404(Receita, idreceita=id)
    ingredientes = ReceitaHasIngrediente.objects.filter(receita=receita)
    return render(request, 'receita/detail.html', {
        'receita': receita,
        'ingredientes': ingredientes
    })

def forum(request):

    topicos = Topico.objects.select_related('usuario', 'categoria').all()
    
    try:
        # Verificar se existem categorias, se não, criar algumas padrão
        if not Categoria.objects.exists():
            categorias_padrao = [
                'Dúvidas Gerais',
                'Alergia a Leite', 
                'Alergia a Ovos',
                'Alergia a Amendoim',
                'Alergia a Trigo',
                'Dicas de Nutrição',
                'Eventos'
            ]
            for nome in categorias_padrao:
                Categoria.objects.create(nome=nome)
        
        # Buscar tópicos - com filtros
        categoria_id = request.GET.get('categoria')
        busca = request.GET.get('busca', '')
        ordenar = request.GET.get('ordenar', 'recentes')
        
        # Query base
        topicos = Topico.objects.all()
        
        # Filtro por categoria
        if categoria_id:
            topicos = topicos.filter(categoria_id=categoria_id)
            categoria_selecionada = Categoria.objects.get(idcategoria=categoria_id)
        else:
            categoria_selecionada = None
        
        # Filtro por busca
        if busca:
            topicos = topicos.filter(titulo__icontains=busca)
        
        # Ordenação
        if ordenar == 'antigos':
            topicos = topicos.order_by('idtopico')
        elif ordenar == 'comentados':
            # Ordenar por número de comentários (mais comentados primeiro)
            topicos = topicos.annotate(num_comentarios=models.Count('postagem')).order_by('-num_comentarios')
        else:  # recentes (padrão)
            topicos = topicos.order_by('-idtopico')
        
        categorias = Categoria.objects.all()
        
        context = {
            'topicos': topicos,
            'categorias': categorias,
            'categoria_selecionada': categoria_selecionada,
            'termo_busca': busca,
            'ordenacao_selecionada': ordenar,
        }
        return render(request, 'forum.html', context)
        
    except Exception as e:
        print(f"Erro na view forum: {e}")
        # Fallback seguro
        context = {
            'topicos': [],
            'categorias': Categoria.objects.all(),
            'categoria_selecionada': None,
            'termo_busca': '',
            'ordenacao_selecionada': 'recentes',
        }
        return render(request, 'forum.html', context)

@login_required
def topico_detail(request, id):
    topico = get_object_or_404(Topico, idtopico=id)
    postagens = Postagem.objects.filter(topico=topico).order_by('data_publicacao')
    
    if request.method == 'POST':
        texto = request.POST.get('texto')
        if texto:
            Postagem.objects.create(
                texto=texto,
                usuario=request.user,
                topico=topico
            )
            messages.success(request, 'Resposta publicada com sucesso!')
            return redirect('topico_detail', id=id)
    
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

def custom_logout(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso!')
    return redirect('index') 

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

@login_required
def criar_topico(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        categoria_id = request.POST.get('categoria')
        conteudo = request.POST.get('conteudo')
        
        if titulo and categoria_id and conteudo:
            try:
                # Verificar se existe um fórum padrão
                forum_padrao = Forum.objects.first()
                if not forum_padrao:
                    forum_padrao = Forum.objects.create(
                        titulo="Fórum Principal",
                        enunciado="Discussões gerais sobre alergias alimentares",
                        data_inicio=timezone.now().strftime("%Y-%m-%d"),
                        usuario=request.user
                    )
                
                categoria = Categoria.objects.get(idcategoria=categoria_id)
                
                # Criar o tópico
                topico = Topico.objects.create(
                    titulo=titulo[:100],  # Limita a 100 caracteres
                    enunciado=conteudo,   # Agora aceita texto longo
                    data_inicio=timezone.now().strftime("%Y-%m-%d"),
                    forum=forum_padrao,
                    categoria=categoria,
                    usuario=request.user
                )
                
                messages.success(request, 'Tópico criado com sucesso!')
                return redirect('forum')
                
            except Exception as e:
                messages.error(request, f'Erro ao criar tópico: {str(e)}')
                # Redireciona de volta para o fórum mantendo os filtros
                return redirect('forum')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return redirect('forum')
    
    # Se for GET, redireciona para o fórum
    return redirect('forum')