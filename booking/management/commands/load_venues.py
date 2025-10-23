from django.core.management.base import BaseCommand
from main.models import Venue
from django.conf import settings
from django.utils.text import slugify
import csv
import os

class Command(BaseCommand):
    help = "Load venues from CSV file"

    def handle(self, *args, **options):
        csv_path = os.path.join(settings.BASE_DIR, "data", "venues - courts_enriched_data.csv")

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"File not found: {csv_path}"))
            return

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                venue, created = Venue.objects.get_or_create(
                    name=row["name"],
                    defaults={
                        "category": row.get("category"),
                        "address": row.get("address"),
                        "price": row.get("price") or None,
                        "capacity": row.get("capacity") or None,
                        "opening_time": row.get("opening_time") or None,
                        "closing_time": row.get("closing_time") or None,
                        "thumbnail": row.get("thumbnail") or "",
                        "slug": slugify(row["name"]),
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Added {venue.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"{venue.name} already exists"))
