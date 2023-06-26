from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100)
    cpf = models.BigIntegerField(unique=True)
    limite_compras = models.DecimalField(max_digits=5, decimal_places=2)
    limite_compras_maximo = models.DecimalField(max_digits=5, decimal_places=2, default=0) # novo campo
    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=150)
    foto_cliente = models.ImageField(upload_to='fotos_cliente/', null=True, blank=True)

    def __str__(self):
        return self.nome
