from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'sobrenome', 'cpf', 'limite_compras', 'telefone', 'endereco', 'foto_cliente']


    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        if self.instance.pk:
            # estamos editando um cliente existente
            if Cliente.objects.filter(cpf=cpf).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("CPF já cadastrado.")
        else:
            # estamos cadastrando um novo cliente
            if Cliente.objects.filter(cpf=cpf).exists():
                raise forms.ValidationError("CPF já cadastrado.")
        return cpf
