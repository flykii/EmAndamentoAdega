from django.shortcuts import render, redirect, get_object_or_404
from .forms import ClienteForm
from .models import Cliente
from decimal import Decimal
from django.contrib import messages



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
        add_value = Decimal(request.POST.get("add_value"))
        action = request.POST.get("action")
        
        if action == "pagar":
            cliente.limite_compras += add_value
            messages.success(request, 'Valor adicionado com sucesso ao limite de compras.')
        elif action == "add_venda":
            cliente.limite_compras -= add_value
            messages.success(request, f'Venda adicionada com sucesso para {cliente.nome}.')
        elif action == "alterar_limite":
            cliente.limite_compras_maximo = add_value
            messages.success(request, 'Limite máximo alterado com sucesso.')
        else:
            messages.error(request, 'Ação desconhecida.')
            return redirect('lista_cliente')
        
        cliente.save()
    return redirect('lista_cliente')

