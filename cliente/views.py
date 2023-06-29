from django.shortcuts import render, redirect, get_object_or_404
from .forms import ClienteForm
from .models import Cliente, Transacao
from decimal import Decimal
from django.contrib import messages
from django.db.models import Sum




def lista_cliente(request):
    clientes = Cliente.objects.all().order_by('-id')
    return render(request, 'lista_cliente.html', {'clientes': clientes})


def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_cliente')
    else:
        form = ClienteForm()
    return render(request, 'template_cliente.html', {'form': form, 'form_action_url': 'cadastrar_cliente'})

def editar_cliente(request, id):
    cliente = Cliente.objects.get(id=id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('lista_cliente')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'template_cliente.html', {'form': form, 'form_action_url': 'editar_cliente', 'cliente_id': id})



    
def deletar_cliente(request, id):
    cliente = Cliente.objects.get(id=id)
    if request.method == 'POST':
        cliente.delete()
        return redirect('lista_cliente')
    else:
        return render(request, 'deletar_cliente.html', {'cliente': cliente})
    
def add_value_to_limit(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "zerar":
            cliente.limite_compras = cliente.limite_compras_maximo
            cliente.save()

            # Zerar o saldo devedor
            vendas = Transacao.objects.filter(cliente=cliente, tipo=Transacao.TIPO_VENDA).aggregate(total_vendas=Sum('valor'))
            pagamentos = Transacao.objects.filter(cliente=cliente, tipo=Transacao.TIPO_PAGAMENTO).aggregate(total_pagamentos=Sum('valor'))

            total_vendas = vendas['total_vendas'] if vendas['total_vendas'] is not None else 0
            total_pagamentos = pagamentos['total_pagamentos'] if pagamentos['total_pagamentos'] is not None else 0

            saldo_devedor = round(total_vendas - total_pagamentos, 2)

            # Verificar se o saldo devedor é negativo e zerá-lo
            if saldo_devedor < 0:
                Transacao.objects.filter(cliente=cliente, tipo=Transacao.TIPO_PAGAMENTO).delete()
            elif saldo_devedor > 0:
                Transacao.objects.filter(cliente=cliente, tipo=Transacao.TIPO_VENDA).delete()

            messages.success(request, 'Limite de compras e saldo devedor zerados com sucesso.')

            return redirect('lista_cliente')

        add_value = Decimal(request.POST.get("add_value"))

        if action == "pagar":
            cliente.limite_compras += add_value
            Transacao.objects.create(cliente=cliente, valor=add_value, tipo=Transacao.TIPO_PAGAMENTO)
            messages.success(request, 'Valor adicionado com sucesso ao limite de compras.')
        elif action == "add_venda":
            if add_value > cliente.limite_compras:
                messages.error(request, 'O valor da venda ultrapassa o limite de compras do cliente.')
                return redirect('lista_cliente')

            cliente.limite_compras -= add_value
            Transacao.objects.create(cliente=cliente, valor=add_value, tipo=Transacao.TIPO_VENDA)
            messages.success(request, f'Venda adicionada com sucesso para {cliente.nome}.')
        elif action == "alterar_limite":
            cliente.limite_compras_maximo = add_value
            messages.success(request, 'Limite máximo alterado com sucesso.')
        else:
            messages.error(request, 'Ação desconhecida.')
            return redirect('lista_cliente')

        cliente.save()

    return redirect('lista_cliente')

def cliente_saldo_devedor(cliente):
    vendas = Transacao.objects.filter(cliente=cliente, tipo=Transacao.TIPO_VENDA).aggregate(total_vendas=Sum('valor'))
    pagamentos = Transacao.objects.filter(cliente=cliente, tipo=Transacao.TIPO_PAGAMENTO).aggregate(total_pagamentos=Sum('valor'))

    total_vendas = vendas['total_vendas'] if vendas['total_vendas'] is not None else 0
    total_pagamentos = pagamentos['total_pagamentos'] if pagamentos['total_pagamentos'] is not None else 0

    saldo_devedor = round(total_vendas - total_pagamentos, 2)

    if saldo_devedor >= 0:
        saldo_devedor = '{:.2f}'.format(saldo_devedor)
    else:
        saldo_devedor = '{:.2f}'.format(abs(saldo_devedor))

    return saldo_devedor



