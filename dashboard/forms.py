from django import forms
from .models import Product, Order

#CRUD-Create Operation
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields =['name', 'category', 'quantity', 'price_each', 'supplier', 'image']

        price_each = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        localize=True, 
        widget=forms.NumberInput(attrs={'placeholder': 'Price per item in NPR', 'class': 'form-control'})
        )
        supplier = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter supplier name/location', 'class': 'form-control'})
        )
        
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['Product', 'order_quantity']

    def clean_order_quantity(self):
        order_quantity = self.cleaned_data.get('order_quantity')
        product = self.cleaned_data.get('Product')

        if order_quantity > product.quantity:
            raise forms.ValidationError(f"The order quantity cannot exceed the available quantity ({product.quantity}).")
        
        return order_quantity