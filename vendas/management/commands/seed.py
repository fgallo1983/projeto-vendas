import random
import datetime
from faker import Faker
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from django.contrib.auth import get_user_model
from vendas.models import Loja, Venda, Produto

fake = Faker('pt_BR')
User = get_user_model()

def get_dias_uteis_do_mes(ano, mes):
    dias = []
    dia = datetime.date(ano, mes, 1)
    while dia.month == mes:
        if dia.weekday() < 5:  # dias de semana (segunda a sexta)
            dias.append(dia)
        dia += datetime.timedelta(days=1)
    return dias

class Command(BaseCommand):
    help = 'Popula o banco com lojas, usuários e vendas fictícias'

    def handle(self, *args, **kwargs):
        produtos = list(Produto.objects.all())
        if not produtos:
            self.stdout.write(self.style.ERROR('Cadastre produtos antes de rodar o seed.'))
            return

        Venda.objects.all().delete()
        Loja.objects.all().delete()
        User.objects.filter(is_staff=False).delete()

        cidades_sp = [
            'São Paulo', 'Campinas', 'Santos', 'São Bernardo do Campo',
            'Ribeirão Preto', 'Sorocaba', 'Guarulhos', 'Osasco', 'Barueri',
            'São José dos Campos', 'Mogi das Cruzes', 'Bauru', 'Jundiaí',
            'Presidente Prudente', 'Franca'
        ]

        # Criar 15 lojas
        lojas = [Loja.objects.create(nome=fake.company(), cidade=random.choice(cidades_sp)) for _ in range(15)]

        # Criar 20 vendedoras
        vendedoras = []
        for _ in range(20):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(100,999)}"
            email = f"{username}@email.com"
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password='123456',
                is_staff=False
            )
            user_lojas = random.sample(lojas, random.randint(1, 3))
            for loja in user_lojas:
                user.lojas.add(loja)
            vendedoras.append((user, user_lojas))

        ano_atual = datetime.date.today().year
        for vendedora, lojas_vendedora in vendedoras:
            for mes in range(1, 13):
                dias_uteis = get_dias_uteis_do_mes(ano_atual, mes)
                random.shuffle(dias_uteis)

                total_pecas_mes = 0
                meta_pecas = random.randint(200, 800)

                while total_pecas_mes < meta_pecas:
                    dia = random.choice(dias_uteis)
                    loja = random.choice(lojas_vendedora)

                    produtos_do_dia = random.sample(produtos, min(len(produtos), random.randint(1, 4)))
                    for produto in produtos_do_dia:
                        if total_pecas_mes >= meta_pecas:
                            break

                        max_restante = meta_pecas - total_pecas_mes
                        quantidade = random.randint(1, min(20, max_restante))

                        try:
                            Venda.objects.create(
                                produto=produto,
                                loja=loja,
                                vendedor=vendedora,
                                quantidade_vendida=quantidade,
                                valor=quantidade * produto.valor,
                                data_venda=dia
                            )
                            total_pecas_mes += quantidade
                        except:
                            continue  # Em caso de conflito de unicidade, ignora e tenta outro

        self.stdout.write(self.style.SUCCESS('Seed executado com sucesso!'))
