from django.shortcuts import render, redirect, get_object_or_404
from .models import Categoria, Produto, Venda
from .forms import CategoriaForm, ProdutoForm, FinalizarVendaForm, VendaForm
from django.contrib import messages
from django.db.models import Count, Sum
from django.db.models import Q
from datetime import datetime
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone
from django.db.models.functions import TruncDay, TruncMonth



def categoria_list(request):
    categorias = Categoria.objects.all()
    return render(request, 'categoria_list.html', {'categorias': categorias})

def categoria_create(request):
    categoria = CategoriaForm(request.POST or None)

    if categoria.is_valid():
        categoria.save()
        return redirect('categoria_list')

    return render(request, 'categoria_form.html', {'categoria': categoria})


def cadastra_atualiza_produto(request, pk=None):
    if pk:
        produto = get_object_or_404(Produto, pk=pk)
    else:
        produto = Produto()

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            # Verificando se nova_categoria foi preenchido
            nova_categoria = form.cleaned_data.get('nova_categoria')
            if nova_categoria:
                # Criando a nova categoria
                categoria, created = Categoria.objects.get_or_create(nome=nova_categoria)
                produto.categoria = categoria
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm(instance=produto)

    return render(request, 'cadastra_atualiza_produto.html', {'form': form})

def lista_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'lista_produtos.html', {'produtos': produtos})

def venda_produto(request):
    carrinho = request.session.get('carrinho', [])
    total = 0
    item_carrinho = {}

    if request.method == "POST":
        form = VendaForm(request.POST)
        if form.is_valid():
            produto = form.cleaned_data['produto']
            quantidade = form.cleaned_data['quantidade']
            subtotal = float(produto.preco_venda) * quantidade
            # Atualizando o estoque
            produto.atualizar_estoque(quantidade)
           
            if produto.camara_fria and produto.quantidade_na_camarafria  and produto.quantidade_atual_camarafria is not None:
                produto.quantidade_atual_camarafria = max(0, produto.quantidade_na_camarafria - quantidade)
                produto.save()

            item_carrinho = {
                'produto_id': produto.id,
                'nome': produto.nome,
                'quantidade': quantidade,
                'preco': float(produto.preco_venda),
                'subtotal': subtotal
            }
            carrinho.append(item_carrinho)
            request.session['carrinho'] = carrinho

            # Criar nova instância de Venda e salvar no banco de dados
            venda = Venda(produto=produto, quantidade=quantidade, vendedor=request.user)
            venda.save()

            # Adicionar id da venda ao item do carrinho
            item_carrinho['venda_id'] = venda.id


    for item in carrinho:  
        total += item['subtotal']

    form = VendaForm()  
    pagamento_form = FinalizarVendaForm() if request.session.get('carrinho') else None

    return render(request, 'venda_produto.html', {'form': form, 'carrinho': carrinho, 'total': total, 'pagamento_form': pagamento_form})


def finalizar_venda(request):
    carrinho = request.session.get('carrinho', [])
    total = 0

    if not carrinho:
        messages.error(request, 'Carrinho vazio')
        return redirect('venda_produto')

    for item in carrinho:
        total += item['subtotal']

    if request.method == "POST":
        form = FinalizarVendaForm(request.POST)
        if form.is_valid():
            forma_pagamento = form.cleaned_data['forma_pagamento']
            # Adicione esta linha para obter o valor_recebido, mesmo que seja None
            valor_recebido = form.cleaned_data.get('valor_recebido')
            for item in carrinho:
                # Buscar a venda usando o id da venda em vez do id do produto
                venda = Venda.objects.get(id=item['venda_id'])
                venda.forma_pagamento = forma_pagamento
                venda.data_venda = timezone.now()
                venda.save()
            
            if forma_pagamento == 'dinheiro':
                if valor_recebido is None or valor_recebido < total:
                    messages.error(request, 'Valor recebido insuficiente')
                else:
                    troco = valor_recebido - total
                    messages.success(request, f'Troco: R${troco:.2f}')
                    for item in carrinho:
                        venda = Venda.objects.get(id=item['venda_id'])

                        venda.forma_pagamento = forma_pagamento
                        venda.save()
                    request.session['carrinho'] = []
                    return redirect('venda_produto')
            else:
                for item in carrinho:
                    venda = Venda.objects.get(id=item['venda_id'])

                    venda.forma_pagamento = forma_pagamento
                    venda.save()
                messages.success(request, 'Venda finalizada com sucesso')
                request.session['carrinho'] = []
                return redirect('venda_produto')

    return render(request, 'finalizar_venda.html', {'form': form, 'total': total})

    

def edita_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if 'delete' in request.POST:
        produto.delete()
        return redirect('lista_produtos')
    elif request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'edita_produto.html', {'form': form, 'produto': produto})


def dashboard(request):
    forma_pagamento = request.GET.get('forma_pagamento')  # Obter o filtro de forma de pagamento do GET request
    mes = request.GET.get('mes')  # Obter o filtro de mês do GET request
    dia = request.GET.get('dia')  # Obter o filtro de dia do GET request
    venda_filter = Q()  # Iniciar o objeto de filtro vazio
    
    if dia:
        dia = datetime.strptime(dia, '%Y-%m-%d').day

    if forma_pagamento:
        venda_filter &= Q(forma_pagamento=forma_pagamento)
    if mes:
        venda_filter &= Q(data__month=mes)
    if dia:
        venda_filter &= Q(data__day=dia)

    vendas_dia = Venda.objects.filter(data=TruncDay(timezone.now())).filter(venda_filter)
    vendas_mes = Venda.objects.filter(data__gte=timezone.now().replace(day=1)).filter(venda_filter)# valores que você quer adicionar
    total_vendas_dia = vendas_dia.count()
    total_vendas_mes = vendas_mes.count()
    total_itens_vendidos_dia = sum(venda.quantidade for venda in vendas_dia) if vendas_dia.exists() else 0
    total_itens_vendidos_mes = sum(venda.quantidade for venda in vendas_mes) if vendas_mes.exists() else 0


    # Item mais vendido e menos vendido (por dia e mês)
    item_mais_vendido_dia = (
        vendas_dia.values('produto__nome')
        .annotate(total=Count('id'))
        .order_by('-total')
        .first()
    )
    item_menos_vendido_dia = (
        vendas_dia.values('produto__nome')
        .annotate(total=Count('id'))
        .order_by('total')
        .first()
    )
    item_mais_vendido_mes = (
        vendas_mes.values('produto__nome')
        .annotate(total=Count('id'))
        .order_by('-total')
        .first()
    )
    item_menos_vendido_mes = (
        vendas_mes.values('produto__nome')
        .annotate(total=Count('id'))
        .order_by('total')
        .first()
    )
    # Quantidade total de itens vendidos (por dia e mês)
    quantidade_total_vendida_dia = Venda.objects.filter(venda_filter).count()
    quantidade_total_vendida_mes = Venda.objects.filter(venda_filter).count()

    # Valor total de todas as vendas (por dia e mês)
    valor_total_vendas_dia = Venda.objects.filter(venda_filter).aggregate(
        credito=Sum('produto__preco_venda', filter=Q(forma_pagamento='credito')),
        debito=Sum('produto__preco_venda', filter=Q(forma_pagamento='debito')),
        pix=Sum('produto__preco_venda', filter=Q(forma_pagamento='pix')),
        dinheiro=Sum('produto__preco_venda', filter=Q(forma_pagamento='dinheiro'))
    )
    valor_total_vendas_mes = Venda.objects.filter(venda_filter).aggregate(
        credito=Sum('produto__preco_venda', filter=Q(forma_pagamento='credito')),
        debito=Sum('produto__preco_venda', filter=Q(forma_pagamento='debito')),
        pix=Sum('produto__preco_venda', filter=Q(forma_pagamento='pix')),
        dinheiro=Sum('produto__preco_venda', filter=Q(forma_pagamento='dinheiro'))
    )

    # Valor das vendas separados (por dia e mês)
    valor_vendas_dia = Venda.objects.filter(venda_filter).values('forma_pagamento').annotate(total=Sum('produto__preco_venda'))
    valor_vendas_mes = Venda.objects.filter(venda_filter).values('forma_pagamento').annotate(total=Sum('produto__preco_venda'))

    context = {
        'total_vendas_dia': total_vendas_dia,
        'total_vendas_mes': total_vendas_mes,
        'total_itens_vendidos_dia': total_itens_vendidos_dia,
        'total_itens_vendidos_mes': total_itens_vendidos_mes,
        'item_mais_vendido_dia': item_mais_vendido_dia,
        'item_menos_vendido_dia': item_menos_vendido_dia,
        'item_mais_vendido_mes': item_mais_vendido_mes,
        'item_menos_vendido_mes': item_menos_vendido_mes,
        'quantidade_total_vendida_dia': quantidade_total_vendida_dia,
        'quantidade_total_vendida_mes': quantidade_total_vendida_mes,
        'valor_total_vendas_dia': valor_total_vendas_dia,
        'valor_total_vendas_mes': valor_total_vendas_mes,
        'valor_vendas_dia': valor_vendas_dia,
        'valor_vendas_mes': valor_vendas_mes,
    }

    return render(request, 'dashboard.html', context)



def listar_vendas(request):
    vendas = Venda.objects.all().order_by('-data')
    return render(request, 'listar_vendas.html', {'vendas': vendas})



def remover_item_carrinho(request, item_index):
    carrinho = request.session.get('carrinho', [])
    if item_index < len(carrinho):
        item = carrinho.pop(item_index)
        produto = Produto.objects.get(id=item['produto_id'])
        produto.estoque += item['quantidade']
        produto.save()
        request.session['carrinho'] = carrinho
    return redirect('venda_produto')
