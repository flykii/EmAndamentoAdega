from django import template
from cliente.views import cliente_saldo_devedor

register = template.Library()

@register.filter
def formatar_cpf(cpf):
    cpf = str(cpf).zfill(11)  # Preenche com zeros à esquerda para garantir 11 dígitos
    return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}'

@register.filter
def formatar_telefone(telefone):
    telefone = str(telefone).zfill(11)
    return f'({telefone[:2]}){telefone[2:3]}.{telefone[3:7]}-{telefone[7:11]}'



@register.filter
def saldo_devedor(cliente):
    return cliente_saldo_devedor(cliente)
