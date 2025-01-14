from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.
CATEGORY = (
    ('Stationary', 'Stationary'),
    ('Electronics', 'Electronics'),
    ('Food', 'Food'),
)
ORDER_STATUS = (
    ('Pending', 'Pending'),
    ('Processing', 'Processing'),
    ('Dispatched', 'Dispatched'),
    ('Completed', 'Completed'),
)

class Product(models.Model):
    name = models.CharField(max_length=100, null=True)
    quantity = models.BigIntegerField(null=True)
    category = models.CharField(max_length=50, choices=CATEGORY, null=True)
    price_each = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    supplier = models.CharField(max_length=200, default="N/A", null=False)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    threshold = models.PositiveIntegerField(default=10)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = 'Staff Product'

    def __str__(self):
        return f'{self.name}-{self.quantity}'
    
    def is_below_threshold(self):
        return self.quantity is not None and self.quantity < self.threshold

class Order(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    staff = models.ForeignKey(User, models.CASCADE, null= True)
    order_quantity = models.PositiveIntegerField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='Pending')

    class Meta:
        verbose_name_plural = 'Order'

    def __str__(self):
        return f'{self.Product} ordered by {self.staff.username}'
    
class Notification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.product.name}'