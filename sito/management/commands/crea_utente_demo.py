from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Crea utente demo per il laboratorio (username: pippo, password: lab2024)'

    def handle(self, *args, **options):
        username = 'pippo'
        password = 'lab2024'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Utente "{username}" esiste già.'))
        else:
            User.objects.create_user(username=username, password=password)
            self.stdout.write(self.style.SUCCESS(f'✓ Utente demo "{username}" creato con successo!'))
            self.stdout.write(f'  Username: {username}')
            self.stdout.write(f'  Password: {password}')
