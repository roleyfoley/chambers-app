from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from config.settings.kms import string_or_b64kms


class Command(BaseCommand):
    help = (
        'Creates new superuser with password provided without any interactive '
        'input. Resets the password for existing user. Password may be either '
        'cleartext value or KMS-encrypted BASE64 secret'
    )

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **kwargs):
        user, created = get_user_model().objects.get_or_create(
            username=kwargs['username']
        )

        user.set_password(string_or_b64kms(kwargs['password']))
        user.is_superuser = True
        user.is_staff = True
        user.save()

        if created:
            self.stdout.write("Complete, user created\n")
        else:
            self.stdout.write("Complete, user password updated\n")
        return
