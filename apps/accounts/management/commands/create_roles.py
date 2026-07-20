from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.accounts.roles import PROJECT_ROLES


class Command(BaseCommand):
    help = "Create TrustLedger role groups."

    def handle(self, *args, **options):
        for role in PROJECT_ROLES:
            Group.objects.get_or_create(name=role)
            self.stdout.write(self.style.SUCCESS(f"Role ready: {role}"))