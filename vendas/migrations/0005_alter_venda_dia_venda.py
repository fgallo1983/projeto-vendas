# Generated by Django 5.1.6 on 2025-03-03 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendas', '0004_venda_dia_venda'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venda',
            name='dia_venda',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
