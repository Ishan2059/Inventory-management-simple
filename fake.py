import os
import django

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventoryproject.settings')  # Replace 'inventoryproject' with your project name
django.setup()

from dashboard.models import Product  # Replace 'dashboard' with your app name
from datetime import datetime, timedelta
import random

# Generate random dates and update products
products = Product.objects.all()

start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 1, 1)

for product in products:
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    product.date = random_date
    product.save()

print("Random dates added to all products.")
