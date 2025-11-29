from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

# Para JSONField - compatível com todas as bases de dados
if hasattr(models, 'JSONField'):
    # Django 3.1+ tem JSONField nativo
    JSONField = models.JSONField
else:
    # Fallback para versões mais antigas ou outros bancos
    try:
        from django.contrib.postgres.fields import JSONField
    except ImportError:
        # Fallback para SQLite e outros bancos
        from django.db.models import TextField
        class JSONField(TextField):
            """Simula JSONField para bancos que não suportam JSON nativo"""
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
            
            def from_db_value(self, value, expression, connection):
                import json
                if value is None:
                    return value
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            
            def get_prep_value(self, value):
                import json
                if value is None:
                    return value
                return json.dumps(value)


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, password=None, perfil='usuario'):
        if not email:
            raise ValueError('Usuários devem ter um endereço de email')
        
        usuario = self.model(
            email=self.normalize_email(email),
            nome=nome,
            perfil=perfil
        )
        
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario
    
    def create_superuser(self, email, nome, password):
        usuario = self.create_user(
            email=email,
            nome=nome,
            password=password,
            perfil='administrador'
        )
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(using=self._db)
        return usuario


class Usuario(AbstractBaseUser):
    idusuario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    perfil = models.CharField(max_length=45, default='usuario')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']
    
    def __str__(self):
        return self.nome
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser


class Alergia(models.Model):
    idalergia = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=45)
    
    def __str__(self):
        return self.nome


class AlergiaHasUsuario(models.Model):
    idusuario_alergia = models.AutoField(primary_key=True)
    alergia = models.ForeignKey(Alergia, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = (('alergia', 'usuario'),)
    
    def __str__(self):
        return f"{self.usuario.nome} - {self.alergia.nome}"


class Categoria(models.Model):
    idcategoria = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=45)
    
    def __str__(self):
        return self.nome


class CategoriaReceita(models.Model):
    idcategoria_receita = models.AutoField(primary_key=True)
    nome_categoria = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome_categoria


class Favorito(models.Model):
    idfavorito = models.AutoField(primary_key=True)
    receita = models.ForeignKey('Receita', on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = (('receita', 'usuario'),)
    
    def __str__(self):
        return f"{self.usuario.nome} - {self.receita.titulo}"


class Forum(models.Model):
    idforum = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    enunciado = models.TextField()
    data_inicio = models.CharField(max_length=45)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.titulo




class Postagem(models.Model):
    idpostagem = models.AutoField(primary_key=True)
    texto = models.TextField(max_length=255)
    data_publicacao = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    topico = models.ForeignKey('Topico', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Postagem {self.idpostagem} - {self.usuario.nome}"


class Receita(models.Model):
    
    DIFICULDADE_CHOICES = [
        ('F', 'Fácil'),
        ('M', 'Médio'),
        ('D', 'Difícil'),
    ]

    idreceita = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=45)
    modo_preparo = models.TextField(max_length=1000)
    ingredientes = models.TextField(max_length=1000)
    porcoes = models.IntegerField()
    categorias_receita = models.ManyToManyField(CategoriaReceita)
    imagem = models.ImageField(upload_to='receitas/', null=True, blank=True)
    tempo_preparo = models.IntegerField(default=0, help_text="Tempo em minutos")
    dificuldade = models.CharField(
        max_length=1,
        choices=DIFICULDADE_CHOICES,
        default='F',
        help_text="Nível de dificuldade da receita"
    )
    
    # ⭐⭐ ADICIONE ESTE CAMPO ⭐⭐
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.titulo



class Topico(models.Model):
    idtopico = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    enunciado = models.TextField()
    data_inicio = models.CharField(max_length=45)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.titulo