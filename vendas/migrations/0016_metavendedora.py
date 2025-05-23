# Generated by Django 5.1.6 on 2025-04-14 14:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendas', '0015_alter_venda_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetaVendedora',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_pecas', models.PositiveIntegerField(verbose_name='Mínimo de Peças')),
                ('max_pecas', models.PositiveIntegerField(blank=True, null=True, verbose_name='Máximo de Peças')),
                ('acrescimo', models.FloatField(verbose_name='Valor do Acréscimo')),
                ('vendedora', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Meta da Vendedora',
                'verbose_name_plural': 'Metas das Vendedoras',
                'ordering': ['min_pecas'],
            },
        ),
    ]
