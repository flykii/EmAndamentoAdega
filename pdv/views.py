from django.shortcuts import render, redirect, get_object_or_404
from .models import Categoria, Produto, Venda
from .forms import CategoriaForm, ProdutoForm, FinalizarVendaForm, VendaForm
from django.contrib import messages
from django.db.models import Sum, Count, F, Func, Q
from django.utils import timezone
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from datetime import datetime
from django.db.models import F
from django.utils import timezone
from cliente.models import Cliente, Transacao
from decimal import Decimal




def categoria_create(request):
    categoria = CategoriaForm(request.POST or None)

    if categoria.is_valid():
        nome_categoria = categoria.cleaned_data['nome']
        if Categoria.objects.filter(nome=nome_categoria).exists():
            categoria.add_error('nome', 'Essa categoria já está cadastrada.')
        else:
            categoria.save()
            return redirect('categoria_list')

    return render(request, 'categoria_form.html', {'categoria': categoria},)

      
def categoria_list(request):
    categorias = Categoria.objects.all().order_by('nome')  # Recupera as categorias ordenadas por nome
    return render(request, 'categoria_list.html', {'categorias': categorias})


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
    produtos = Produto.objects.all().order_by('-id')
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

            if produto.camara_fria and produto.quantidade_na_camarafria and produto.quantidade_atual_camarafria is not None:
                produto.quantidade_atual_camarafria = max(0, produto.quantidade_na_camarafria - quantidade)
                produto.save()

            item_carrinho = {
                'produto_id': produto.id,
                'nome': produto.nome,
                'quantidade': quantidade,
                'preco': float(produto.preco_venda),
                'subtotal': subtotal
            }
            carrinho.insert(0, item_carrinho)
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

    # Obter todos os clientes
    clientes = Cliente.objects.all().order_by('-id')

    return render(request, 'venda_produto.html', {'form': form, 'carrinho': carrinho, 'total': total, 
                                                  'pagamento_form': pagamento_form, 'clientes': clientes})

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
            valor_recebido = form.cleaned_data.get('valor_recebido')
            cliente = form.cleaned_data.get('cliente')  # Obter o cliente selecionado diretamente

            for item in carrinho:
                venda = Venda.objects.get(id=item['venda_id'])
                venda.forma_pagamento = forma_pagamento
                venda.cliente = cliente
                venda.data_venda = timezone.now()
                venda.save()

            if forma_pagamento == 'dinheiro':
                if valor_recebido is None or valor_recebido < total:
                    messages.error(request, 'Valor recebido insuficiente')
                    return redirect('finalizar_venda')
                else:
                    troco = valor_recebido - total
                    messages.success(request, f'Troco: R${troco:.2f}')
            elif forma_pagamento == 'cliente':
                if cliente is None:
                    messages.error(request, 'Selecione um cliente')
                    return redirect('finalizar_venda')
                else:
                    # Atualizar o limite de compras do cliente
                    if total > cliente.limite_compras:
                        messages.error(request, 'O valor total ultrapassa o limite de compras do cliente')
                        return redirect('finalizar_venda')
                    else:
                        cliente.limite_compras -= Decimal(total)
                        Transacao.objects.create(cliente=cliente, valor=total, tipo=Transacao.TIPO_VENDA)
                        messages.success(request, f'Venda adicionada com sucesso para {cliente.nome}.')
            
                        cliente.save()

            for item in carrinho:
                venda = Venda.objects.get(id=item['venda_id'])
                venda.forma_pagamento = forma_pagamento
                venda.save()

            request.session['carrinho'] = []
            messages.success(request, 'Venda finalizada com sucesso')
            return redirect('venda_produto')

    form = FinalizarVendaForm()
    
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


class TruncDate(Func):
    function = 'DATE'
    arity = 1


def dashboard(request):
    forma_pagamento = request.GET.get('forma_pagamento')
    mes = request.GET.get('mes')
    dia = request.GET.get('dia')
    venda_filter = Q()
    custo_total_produtos = calcular_custo_total_produtos()
    data_atual = timezone.now().date()

    if dia:
        dia = datetime.strptime(dia, '%Y-%m-%d').day

    if forma_pagamento:
        venda_filter &= Q(forma_pagamento=forma_pagamento)
    if mes:
        venda_filter &= Q(data__month=mes)
    if dia:
        venda_filter &= Q(data__day=dia)

    vendas_dia = Venda.objects.filter(data=TruncDay(timezone.now())).filter(venda_filter)
    vendas_mes = Venda.objects.filter(data__gte=timezone.now().replace(day=1)).filter(venda_filter)
    vendas_ano = Venda.objects.filter(data__year=timezone.now().year).filter(venda_filter)
    vendas_geral = Venda.objects.filter(venda_filter)

    total_vendas_dia = round(vendas_dia.aggregate(total=Sum('total_venda')).get('total') or 0, 2)
    total_vendas_mes = round(vendas_mes.aggregate(total=Sum('total_venda')).get('total') or 0, 2)
    total_vendas_ano = round(vendas_ano.aggregate(total=Sum('total_venda')).get('total') or 0, 2)
    total_vendas_geral = round(vendas_geral.aggregate(total=Sum('total_venda')).get('total') or 0, 2)

    total_itens_vendidos_dia = round(vendas_dia.aggregate(total=Sum('quantidade')).get('total') or 0, 2)
    total_itens_vendidos_mes = round(vendas_mes.aggregate(total=Sum('quantidade')).get('total') or 0, 2)
    total_itens_vendidos_ano = round(vendas_ano.aggregate(total=Sum('quantidade')).get('total') or 0, 2)
    total_itens_vendidos_geral = round(vendas_geral.aggregate(total=Sum('quantidade')).get('total') or 0, 2)

    ticket_medio_dia = round(total_vendas_dia / total_itens_vendidos_dia, 2) if total_itens_vendidos_dia else 0
    ticket_medio_mes = round(total_vendas_mes / total_itens_vendidos_mes, 2) if total_itens_vendidos_mes else 0
    ticket_medio_ano = round(total_vendas_ano / total_itens_vendidos_ano, 2) if total_itens_vendidos_ano else 0
    ticket_medio_geral = round(total_vendas_geral / total_itens_vendidos_geral, 2) if total_itens_vendidos_geral else 0

    lucro_real = round(vendas_geral.aggregate(total=Sum('produto__lucro_reais')).get('total') or 0, 2)
    media_itens_vendidos = round(vendas_geral.aggregate(media=Count('produto') * 100 / vendas_geral.count()).get('media') or 0, 2)
    
    #total venda DEBITO
    total_vendas_debito = Venda.objects.filter(forma_pagamento='debito').aggregate(
        total_vendas_debito=Sum('total_venda')
    )
    total_vendas_debito = total_vendas_debito['total_vendas_debito']
    
    #total venda CREDITO
    total_vendas_credito = Venda.objects.filter(forma_pagamento='credito').aggregate(
        total_vendas_credito=Sum('total_venda')
    )
    total_vendas_credito = total_vendas_credito['total_vendas_credito']

    #total venda PIX
    total_vendas_pix = Venda.objects.filter(forma_pagamento='pix').aggregate(
        total_vendas_pix=Sum('total_venda')
    )
    total_vendas_pix = total_vendas_pix['total_vendas_pix']

    #total venda DINHEIRO
    total_vendas_dinheiro = Venda.objects.filter(forma_pagamento='dinheiro').aggregate(
        total_vendas_dinheiro=Sum('total_venda')
    )
    total_vendas_dinheiro = total_vendas_dinheiro['total_vendas_dinheiro']

    #total venda CLIENTE
    total_vendas_cliente = Venda.objects.filter(forma_pagamento='cliente').aggregate(
        total_vendas_cliente=Sum('total_venda')
    )
    total_vendas_cliente = total_vendas_cliente['total_vendas_cliente']

    # Calcula a quantidade total de cada produto vendido
    produtos = Venda.objects.values('produto__nome').annotate(
        quantidade_total=Sum('quantidade'),
        valor_total=Sum('total_venda')
    ).order_by('-quantidade_total')

    # Pega o produto mais vendido
    produto_mais_vendido = produtos.first()

    # Pega o produto menos vendido
    produto_menos_vendido = produtos.last()

    valor_vendas_dia = vendas_dia.values('forma_pagamento').annotate(total=Sum('total_venda'))
    valor_vendas_mes = vendas_mes.values('forma_pagamento').annotate(total=Sum('total_venda'))

    soma_total_produtos_preco_compra = round(Produto.objects.aggregate(soma=Sum('preco_compra') * F('estoque')).get('soma') or 0, 2)
    soma_total_produtos_preco_venda = round(Produto.objects.aggregate(soma=Sum('preco_venda') * F('estoque')).get('soma') or 0, 2)
    soma_total_produtos_lucro_reais = round(Produto.objects.aggregate(soma=Sum('lucro_reais') * F('estoque')).get('soma') or 0, 2)
    
    

    

    context = {
        'data_atual': data_atual,
        'total_vendas_dia': total_vendas_dia,
        'total_vendas_mes': total_vendas_mes,
        'total_vendas_ano': total_vendas_ano,
        'total_vendas_geral': total_vendas_geral,
        'total_itens_vendidos_dia': total_itens_vendidos_dia,
        'total_itens_vendidos_mes': total_itens_vendidos_mes,
        'total_itens_vendidos_ano': total_itens_vendidos_ano,
        'total_itens_vendidos_geral': total_itens_vendidos_geral,
        'ticket_medio_dia': ticket_medio_dia,
        'ticket_medio_mes': ticket_medio_mes,
        'ticket_medio_ano': ticket_medio_ano,
        'ticket_medio_geral': ticket_medio_geral,
        'lucro_real': lucro_real,
        'total_vendas_debito': total_vendas_debito,
        'total_vendas_credito': total_vendas_credito,
        'total_vendas_pix': total_vendas_pix,
        'total_vendas_dinheiro': total_vendas_dinheiro,
        'total_vendas_cliente': total_vendas_cliente,
        'produto_mais_vendido': produto_mais_vendido,
         'produto_menos_vendido': produto_menos_vendido,

        'valor_vendas_dia': valor_vendas_dia,
        'valor_vendas_mes': valor_vendas_mes,
        'soma_total_produtos_preco_compra': soma_total_produtos_preco_compra,
        'soma_total_produtos_preco_venda': soma_total_produtos_preco_venda,
        'soma_total_produtos_lucro_reais': soma_total_produtos_lucro_reais,
        'custo_total_produtos': custo_total_produtos,
    }
    return render(request, 'dashboard.html', context)


def calcular_custo_total_produtos():
        produtos = Produto.objects.all()
        custo_total = 0

        for produto in produtos:
            custo_total += produto.estoque * produto.preco_venda

        return custo_total


def listar_vendas(request):
    vendas = Venda.objects.filter(forma_pagamento__isnull=False).order_by('-data')
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


def buscar_produto(request):
    query = request.GET.get('q', '')  # Obtém o termo de busca do parâmetro GET 'q'
    produtos = Produto.objects.filter(nome__icontains=query) 
    return render(request, 'lista_produtos.html', {'produtos': produtos})
