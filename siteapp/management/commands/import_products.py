import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from siteapp.models import Category, Product, ProductVariant


class Command(BaseCommand):
    help = "Import products + with/without-blouse variants from CSV"

    def handle(self, *args, **options):
        # CSV path: siteapp/data/products.csv
        base_dir = Path(__file__).resolve().parent.parent.parent  # -> siteapp/
        csv_path = base_dir / "data" / "products.csv"

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"CSV file not found: {csv_path}"))
            return

        self.stdout.write(f"Reading: {csv_path}")

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                title = row["title"].strip()
                slug = row["slug"].strip()
                category_name = row["category"].strip()
                description = row["description"].strip()
                base_price = row["base_price"].strip()

                with_blouse_price = row["variant_with_blouse_price"].strip()
                with_blouse_stock = int(row["variant_with_blouse_stock"])
                without_blouse_price = row["variant_without_blouse_price"].strip()
                without_blouse_stock = int(row["variant_without_blouse_stock"])

                # Category: your Category model has name + slug
                category_slug = slugify(category_name)
                category, _ = Category.objects.get_or_create(
                    slug=category_slug,
                    defaults={"name": category_name},
                )

                # Product
                product, created_prod = Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "title": title,
                        "description": description,
                        "category": category,
                        "base_price": base_price,
                        "active": True,
                    },
                )

                if created_prod:
                    self.stdout.write(self.style.SUCCESS(f"Created product: {product.title}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Product already exists, updating variants: {product.title}"))

                # Variant 1: WITH BLOUSE
                ProductVariant.objects.update_or_create(
                    product=product,
                    blouse_option="with_blouse",
                    defaults={
                        "price": with_blouse_price,
                        "stock": with_blouse_stock,
                        "sku": "",
                        "color": "",
                    },
                )

                # Variant 2: WITHOUT BLOUSE
                ProductVariant.objects.update_or_create(
                    product=product,
                    blouse_option="without_blouse",
                    defaults={
                        "price": without_blouse_price,
                        "stock": without_blouse_stock,
                        "sku": "",
                        "color": "",
                    },
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f" → Variants synced for: {product.title} "
                        f"(with blouse: {with_blouse_stock}, without blouse: {without_blouse_stock})"
                    )
                )

        self.stdout.write(self.style.SUCCESS("✅ Import complete."))
