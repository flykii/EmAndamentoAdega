# Generated by Django 4.2 on 2023-05-09 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('ADMIN', 'Admin'), ('GERENTE', 'Gerente'), ('FUNCIONARIO', 'Funcionário')], default='FUNCIONARIO', max_length=17, verbose_name='Perfil de usuário'),
        ),
    ]
