# export_products_to_csv.py

import csv
from django.core.management.base import BaseCommand
from dashboard.models import Product  # Replace with your app and model name

class Command(BaseCommand):
    help = 'Export product data to CSV'

    def handle(self, *args, **kwargs):
        # Define the CSV file path
        csv_file = 'product_data.csv'

        # Fetch all product data from the database
        products = Product.objects.all()

        # Write data to the CSV file
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write header row
            writer.writerow(['id', 'name', 'quantity', 'category', 'price_each', 'supplier', 'date'])

            # Write product rows
            for product in products:
                writer.writerow([product.id, product.name, product.quantity, product.category, 
                                 product.price_each, product.supplier, product.date])

        self.stdout.write(self.style.SUCCESS(f'Data exported to {csv_file} successfully!'))
