from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    preco_compra = models.DecimalField(max_digits=8, decimal_places=2)
    porcentagem_lucro = models.DecimalField(max_digits=5, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=8, decimal_places=2)
    lucro_reais = models.DecimalField(max_digits=8, decimal_places=2)
    codigo_barras = models.CharField(max_length=50, null=True, blank=True)
    estoque = models.IntegerField()
    camara_fria = models.BooleanField(default=False)
    quantidade_na_camarafria = models.IntegerField(null=True, blank=True)  # quantidade máxima
    quantidade_atual_camarafria = models.IntegerField(default=0)  # quantidade atual
    
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)

    def __str__(self):
        return self.nome
    
    def atualizar_estoque(self, quantidade, reposicao=False):
        if reposicao:
            self.estoque += quantidade
        else:
            if self.estoque >= quantidade:
                self.estoque -= quantidade
            else:
                raise ValueError("Quantidade excede o estoque disponível")
        self.save()

    def vender_produto(self, quantidade):
        self.atualizar_estoque(quantidade)
   
    @property
    def diferenca_quantidade(self):
        if self.quantidade_atual_camarafria is not None and self.quantidade_na_camarafria is not None:
            return self.quantidade_na_camarafria - self.quantidade_atual_camarafria
        else:
            nao = 'Não'
            return nao


class Venda(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    forma_pagamento = models.CharField(max_length=20)
    data = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Venda de {self.produto.nome} - {self.quantidade} unidades"
