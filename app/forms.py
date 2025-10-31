from django import forms
from .models import Receita, CategoriaReceita

class ReceitaForm(forms.ModelForm):
    # Adicionar explicitamente o campo ManyToMany
    categorias_receita = forms.ModelMultipleChoiceField(
    queryset=CategoriaReceita.objects.all(),
    widget=forms.SelectMultiple(attrs={'class': 'form-select'}),  # Select múltiplo
    required=True,
    label="Categorias"
)
    
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
            'tempo_preparo': forms.NumberInput(attrs={'class': 'form-control'}),
        }