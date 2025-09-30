from typing import Any
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Initialize database with migrations and create superuser if needed"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--create-superuser",
            action="store_true",
            help="Create a superuser account",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Starting database initialization...")

        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(
                self.style.SUCCESS("Database connection successful")
            )

            # Run migrations
            self.stdout.write("Running database migrations...")
            call_command("migrate", verbosity=0)
            self.stdout.write(
                self.style.SUCCESS("Database migrations completed")
            )

            # Create superuser if requested
            if options["create_superuser"]:
                self.stdout.write("Creating superuser...")
                call_command("createsuperuser", interactive=False)
                self.stdout.write(self.style.SUCCESS("Superuser created"))

            self.stdout.write(
                self.style.SUCCESS(
                    "Database initialization completed successfully!"
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Database initialization failed: {str(e)}")
            )
            raise
