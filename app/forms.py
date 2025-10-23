from django import forms
from .models import Receita, CategoriaReceita

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['titulo', 'modo_preparo', 'ingredientes', 'porcoes', 
                 'categorias_receita', 'imagem', 'tempo_preparo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Título da receita'
            }),
            'modo_preparo': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Modo de preparo'
            }),
            'ingredientes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Ingredientes, um por linha'
            }),
            'porcoes': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria_receita': forms.Select(attrs={'class': 'form-select'}),
            'tempo_preparo': forms.NumberInput(attrs={'class': 'form-control'}),
        }