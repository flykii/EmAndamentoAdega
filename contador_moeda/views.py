from django.shortcuts import render
from django.contrib import messages
from datetime import datetime

def data_hora(request):
    data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    context = {'data_hora_atual': data_hora_atual}
    return context

# Create your views here.
def contador_moeda(request):
    context = {
        'moeda_5': 0,
        'moeda_10': 0,
        'moeda_25': 0,
        'moeda_50': 0,
        'moeda_1': 0,

        'cinco_centavos': 0,
        'dez_centavos': 0,
        'vinte_cinco_centavos': 0,
        'cinquenta_centavos': 0,
        'um_real': 0,

        'nota_2': 0,
        'nota_5': 0,
        'nota_10': 0,
        'nota_20': 0,
        'nota_50': 0,
        'nota_100': 0,

        'dois_reais': 0,
        'cinco_reais': 0,
        'dez_reais':0,
        'vinte_reais': 0,
        'cinquenta_reais': 0,
        'cem_reais': 0,
    }
    if request.method == 'GET':
        return render(request, 'contador_moeda.html')
    elif request.method == 'POST':
        cinco_centavos = int(request.POST.get('cinco_centavos',0))
        dez_centavos = int(request.POST.get('dez_centavos',0))
        vinte_cinco_centavos = int(request.POST.get('vinte_cinco_centavos',0))
        cinquenta_centavos = int(request.POST.get('cinquenta_centavos',0))
        um_real = int(request.POST.get('um_real', 0))

        dois_reais = int(request.POST.get('dois_reais',0)) 
        cinco_reais = int(request.POST.get('cinco_reais',0)) 
        dez_reais = int(request.POST.get('dez_reais',0)) 
        vinte_reais = int(request.POST.get('vinte_reais',0)) 
        cinquenta_reais = int(request.POST.get('cinquenta_reais',0)) 
        cem_reais = int(request.POST.get('cem_reais',0)) 
        

        # Realiza o cálculo
        moeda_5 = cinco_centavos * 0.05
        moeda_10 = dez_centavos * 0.10
        moeda_25 = vinte_cinco_centavos * 0.25
        moeda_50 = cinquenta_centavos * 0.50
        moeda_1 = um_real * 1
        total_moedas = (cinco_centavos * 0.05) + (dez_centavos * 0.10) + (vinte_cinco_centavos * 0.25) + (cinquenta_centavos * 0.50) + um_real

        nota_2 = dois_reais * 2
        nota_5 = cinco_reais * 5
        nota_10 = dez_reais * 10
        nota_20 = vinte_reais * 20
        nota_50 = cinquenta_reais * 50
        nota_100 = cem_reais * 100
        total_cedulas = (dois_reais * 2) + (cinco_reais * 50) + (dez_reais * 10) + (vinte_reais * 20) + (cinquenta_reais * 50) + (cem_reais * 100)

        cedulas_moedas = total_cedulas + total_moedas
        
        
        
        context['moeda_5'] = moeda_5
        context['moeda_10'] = moeda_10
        context['moeda_25'] = moeda_25
        context['moeda_50'] = moeda_50
        context['moeda_1'] = moeda_1
        context['cinco_centavos'] = cinco_centavos
        context['dez_centavos'] = dez_centavos
        context['vinte_cinco_centavos'] = vinte_cinco_centavos
        context['cinquenta_centavos'] = cinquenta_centavos
        context['um_real'] = um_real

        context['nota_2'] = nota_2
        context['nota_5'] = nota_5
        context['nota_10'] = nota_10
        context['nota_20'] = nota_20
        context['nota_50'] = nota_50
        context['nota_100'] = nota_100
        context['dois_reais'] = dois_reais
        context['cinco_reais'] = cinco_reais
        context['dez_reais'] = dez_reais
        context['vinte_reais'] = vinte_reais
        context['cinquenta_reais'] = cinquenta_reais
        context['cem_reais'] = cem_reais

        # Adiciona uma mensagem com o valor total
        messages.info(request, f"total de moedas é: R$ {total_moedas:.2f}")
        messages.info(request, f"total de cedulas é: R$ {total_cedulas:.2f}")
        messages.success(request, f"total de Notas e Moedas é: R$ {cedulas_moedas:.2f}")
    return render(request, 'contador_moeda.html', context)


from django.shortcuts import render

def calcular_preco(request):
    if request.method == 'GET':
        return render(request, 'calcular_preco.html')
    elif request.method == 'POST':
        preco_produto = float(request.POST.get('preco_produto').replace(',', '.'))

        precos_venda = {}
        
        for i in range(15, 46):
            porcentagem = 1 - (i / 100)
            porcentagens = preco_produto / porcentagem
            preco_venda = f'{porcentagens:.2f}'
            precos_venda[i] = preco_venda
    
    return render(request, 'calcular_preco.html', {'precos_venda': precos_venda, 'preco_produto': preco_produto})





        
        
     
