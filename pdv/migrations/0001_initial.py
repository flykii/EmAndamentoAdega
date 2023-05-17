# Generated by Django 4.2 on 2023-05-09 22:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.TextField()),
                ('preco_compra', models.DecimalField(decimal_places=2, max_digits=8)),
                ('porcentagem_lucro', models.DecimalField(decimal_places=2, max_digits=5)),
                ('preco_venda', models.DecimalField(decimal_places=2, max_digits=8)),
                ('lucro_reais', models.DecimalField(decimal_places=2, max_digits=8)),
                ('codigo_barras', models.CharField(blank=True, max_length=50, null=True)),
                ('estoque', models.IntegerField()),
                ('camara_fria', models.BooleanField(default=False)),
                ('imagem', models.ImageField(blank=True, null=True, upload_to='produtos/')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pdv.categoria')),
            ],
        ),
    ]
