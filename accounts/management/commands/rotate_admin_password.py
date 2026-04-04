import secrets
import string

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Rotate admin password and print the new one.'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help='Admin username to rotate password for')
        parser.add_argument('--length', type=int, default=24, help='Generated password length (default: 24)')

    def handle(self, *args, **options):
        username = options['username']
        length = max(16, options['length'])
        alphabet = string.ascii_letters + string.digits + '#$!@%*_-+'
        new_password = ''.join(secrets.choice(alphabet) for _ in range(length))

        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f'User not found: {username}') from exc

        if not user.is_staff:
            raise CommandError(f'User {username} is not staff/admin.')

        user.set_password(new_password)
        user.save(update_fields=['password'])

        self.stdout.write(self.style.SUCCESS(f'Password rotated for {username}'))
        self.stdout.write(self.style.WARNING(f'NEW_PASSWORD={new_password}'))
