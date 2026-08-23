from django.conf import settings
from django.core.management.base import BaseCommand
from accounts.models import User
from activitylog.utils import record_activity


class Command(BaseCommand):
    help = 'Creates the first admin account from SEED_ADMIN_* settings, if it does not exist yet.'

    def handle(self, *args, **options):
        email = settings.SEED_ADMIN_EMAIL
        if User.objects.filter(email=email).exists():
            self.stdout.write(f'Seed admin already exists: {email}')
            return

        admin = User.objects.create_user(
            email=email,
            name=settings.SEED_ADMIN_NAME,
            password=settings.SEED_ADMIN_PASSWORD,
            role='ADMIN',
            is_staff=True,
            is_superuser=True,
        )

        record_activity(
            action='SEED',
            entity_type='User',
            entity_id=str(admin.id),
            actor=admin,
            details={'note': 'Initial admin account created by seed_admin command'},
        )

        self.stdout.write(self.style.SUCCESS(f'Created seed admin: {email} (password: {settings.SEED_ADMIN_PASSWORD})'))
