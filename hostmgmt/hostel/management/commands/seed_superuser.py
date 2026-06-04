from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a default superuser for PRAVAAH admin access (for development)'

    def handle(self, *args, **kwargs):
        username = 'admin'
        password = 'admin123'
        email    = 'admin@pravaah.edu'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f'Superuser "{username}" already exists. Skipping.'
            ))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Superuser created:\n'
            f'  Username : {username}\n'
            f'  Password : {password}\n'
            f'  Admin    : http://127.0.0.1:8000/admin/\n\n'
            f'  IMPORTANT: Change this password immediately in production!'
        ))
