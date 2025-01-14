from django.contrib import admin
from .models import Product, Order
from django.contrib.auth.models import Group

admin.site.site_header="Inventory management Dashboard"

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category' , 'quantity')
    list_filter = ['category']

class OrderAdmin(admin.ModelAdmin):
    list_display = ('Product', 'staff', 'order_quantity', 'status', 'date') 
    list_filter = ('status',)
    search_fields = ('Product__name', 'staff__username')

# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
# admin.site.unregister(Group)