from django import forms
from .models import Produto, Categoria, Venda

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']

class ProdutoForm(forms.ModelForm):
    descricao = forms.CharField(widget=forms.TextInput(attrs={'size': '40'}))
    
    class Meta:
        model = Produto
        fields = ['nome', 'embalagem', 'unidade_medida', 
                  'descricao', 'categoria','preco_compra', 
                  'porcentagem_lucro', 'preco_venda', 'lucro_reais',
                  'codigo_barras', 'estoque', 'camara_fria',
                  'quantidade_na_camarafria','imagem',]


class VendaForm(forms.Form):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(estoque__gt=0), 
        label="Produto"
    )
    quantidade = forms.IntegerField(min_value=1, label="Quantidade")


class FinalizarVendaForm(forms.Form):    
    forma_pagamento = forms.ChoiceField(choices=Venda.FORMAS_PAGAMENTO, widget=forms.RadioSelect)
    valor_recebido = forms.FloatField(required=False, min_value=0, widget=forms.NumberInput(attrs={'class': 'dinheiro'}))



class MesFiltroForm(forms.Form):
    mes_choices = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    mes = forms.ChoiceField(choices=mes_choices, label='Mês')

class DiaFiltroForm(forms.Form):
    dia = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Dia')

