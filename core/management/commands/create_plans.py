from django.core.management.base import BaseCommand
from core.models import Plan


class Command(BaseCommand):
    help = 'Cria os planos de assinatura padrão'

    def handle(self, *args, **options):
        plans_data = [
            {'tier': 'free', 'name': 'Gratuito', 'monthly_price': 0, 'max_pets': 10, 'max_services': 3, 'max_employees': 1, 'features': ['basic_calendar', 'pet_management'], 'is_default': True, 'order': 0},
            {'tier': 'starter', 'name': 'Iniciante', 'monthly_price': 4900, 'max_pets': 50, 'max_services': 10, 'max_employees': 3, 'features': ['basic_calendar', 'pet_management', 'reports'], 'order': 1},
            {'tier': 'pro', 'name': 'Profissional', 'monthly_price': 9700, 'max_pets': 200, 'max_services': 50, 'max_employees': 10, 'features': ['basic_calendar', 'pet_management', 'reports', 'whatsapp'], 'order': 2},
            {'tier': 'enterprise', 'name': 'Enterprise', 'monthly_price': 19700, 'max_pets': -1, 'max_services': -1, 'max_employees': -1, 'features': ['all'], 'order': 3},
        ]

        for p in plans_data:
            Plan.objects.update_or_create(tier=p['tier'], defaults=p)

        self.stdout.write(self.style.SUCCESS('Planos criados com sucesso!'))