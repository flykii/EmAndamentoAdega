from django.core.management.base import BaseCommand
from faker import Faker
from pdv.models import Categoria, Produto

class Command(BaseCommand):
    help = 'Cria dados fictícios para testes'

    def handle(self, *args, **options):
        fake = Faker('pt_BR')  # Use 'pt_BR' para dados em português

        # Cria novas categorias
        for _ in range(10):
            Categoria.objects.create(
                nome=fake.word(),
            )

        # Cria novos produtos
        for _ in range(50):
            Produto.objects.create(
                nome=fake.word(),
                descricao=fake.sentence(),
                categoria=Categoria.objects.order_by('?').first(),
                preco_compra=fake.random_number(digits=2, fix_len=True),
                porcentagem_lucro=fake.random_number(digits=2, fix_len=True),
                preco_venda=fake.random_number(digits=2, fix_len=True),
                lucro_reais=fake.random_number(digits=2, fix_len=True),
                codigo_barras=fake.unique.random_number(digits=13),
                estoque=fake.random_int(min=0, max=100),
                camara_fria=fake.boolean(),
                quantidade_na_camarafria=fake.random_int(min=0, max=100),
                quantidade_atual_camarafria=fake.random_int(min=0, max=100),
                # não estamos lidando com o campo 'imagem' neste exemplo
            )

        self.stdout.write(self.style.SUCCESS('Dados fictícios criados com sucesso'))
