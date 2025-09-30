"""
Management command to run tests locally with mocked database
Usage: python manage.py test_local
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
import sys


class Command(BaseCommand):
    help = "Run tests locally with in-memory SQLite database"

    def handle(self, *args, **options):
        # Set test settings
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE", "personal_info_api.test_settings"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "🚀 Running tests with in-memory SQLite database..."
            )
        )

        try:
            # Run tests with verbosity
            call_command("test", verbosity=2, *args)
            self.stdout.write(self.style.SUCCESS("✅ All tests passed!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Tests failed: {e}"))
            sys.exit(1)
