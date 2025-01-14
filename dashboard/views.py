from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Notification
from .forms import ProductForm, OrderForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
import json
from .models import Notification
from django.conf import settings
import joblib
from datetime import datetime, timedelta
from django.core.mail import send_mail
import numpy as np

def merge_sort(arr, key):
    if len(arr) > 1:
        mid = len(arr) // 2 # Divide
        left = arr[:mid]  # Left half
        right = arr[mid:]  # Right half

        #sorting both half
        merge_sort(left, key)
        merge_sort(right, key)

        i = j = k = 0

        # COnquEr
        while i < len(left) and j < len(right):

            if getattr(left[i], key) < getattr(right[j], key):
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1

        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1
    return arr

@login_required
def index(request):

    aggregated_orders = Order.objects.values('Product__name').annotate(total_quantity=Sum('order_quantity'))

    products = Product.objects.all()
    order_count = Order.objects.count()
    products_count = products.count()
    workers_count = User.objects.count()
    notification_count = Notification.objects.filter(is_read=0).count()

    product_names = [product.name for product in products]
    product_quantities = [product.quantity for product in products]

    orders = Order.objects.filter(staff=request.user)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.staff = request.user
            instance.save()
            return redirect('dashboard-index')
    else:
        form = OrderForm()

    context = {
        'aggregated_orders': aggregated_orders, 
        'orders': orders,
        'form': form,
        'products': products,
        'products_count': products_count,
        'workers_count': workers_count,
        'notifications_count': notification_count,
        'orders_count': order_count,
        'product_names': json.dumps(product_names),
        'product_quantities': json.dumps(product_quantities),
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def staff(request):
    workers = User.objects.all()
    workers_count = workers.count()
    orders_count = Order.objects.all().count()
    products_count = Product.objects.all().count()
    notification_count = Notification.objects.filter(is_read=0).count()
    
    context={
        'workers': workers,
        'workers_count': workers_count,
        'orders_count':orders_count,
        'products_count':products_count,
        'notifications_count': notification_count,
    }
    return render(request, 'dashboard/staff.html', context)

@login_required
def staff_detail(request, pk):
    workers = User.objects.get(id=pk)
    workers_count = User.objects.all().count()
    orders_count = Order.objects.all().count()
    products_count = Product.objects.all().count()
    context = {
        'workers': workers,
        'workers_count': workers_count,
        'orders_count':orders_count,
        'products_count':products_count,
    }
    return render(request, 'dashboard/staff_detail.html', context)

@login_required
def product(request):
    items = Product.objects.all()

    sort_option = request.GET.get('sort', 'name') 
    items_list = list(items)
    sorted_items = merge_sort(items_list, sort_option)

    products_count = len(sorted_items)
    workers_count = User.objects.all().count()
    orders_count = Order.objects.all().count()
    notification_count = Notification.objects.filter(is_read=0).count()
    
    # CRUD INSERT
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product_name = form.cleaned_data.get('name')
            product_quantity = form.cleaned_data.get('quantity')
            product_price_each = form.cleaned_data.get('price_each')
            product_supplier = form.cleaned_data.get('supplier')
            product_category = form.cleaned_data.get('category')

            # getting product name to check
            existing_product = Product.objects.filter(name=product_name).first()

            if existing_product:
                # checking if the other details match to update quantity
                if (existing_product.price_each == product_price_each and 
                    existing_product.supplier == product_supplier and 
                    existing_product.category == product_category):
                    existing_product.quantity += product_quantity
                    existing_product.save()
                    messages.success(request, f'{product_name} quantity has been updated.')
                else:
                    # If details do not match, create a new product
                    new_product = form.save()
                    messages.success(request, f'{product_name} has been added with new details.')

                    # Email mechanism because if the product added is less we need to send email
                    if new_product.quantity < 10:
                        admin_emails = User.objects.filter(is_superuser=True).values_list('email', flat=True)
                        if admin_emails:
                            send_mail(
                                'Low Stock Alert',
                                f'The product "{new_product.name}" has low stock! Only {new_product.quantity} remaining.',
                                settings.EMAIL_HOST_USER,  
                                list(admin_emails), 
                                fail_silently=False,
                            )
            else:
                # create a new product if it doesnt exist
                new_product = form.save()
                messages.success(request, f'{product_name} has been added.')

                # email mechanism
                if new_product.quantity < 10:
                    admin_emails = User.objects.filter(is_superuser=True).values_list('email', flat=True)
                    if admin_emails:
                        send_mail(
                            'Low Stock Alert',
                            f'The product "{new_product.name}" has low stock! Only {new_product.quantity} remaining.',
                            settings.EMAIL_HOST_USER,  # Your email
                            list(admin_emails),  # Admin's email
                            fail_silently=False,
                        )

            return redirect('dashboard-product')
    else:
        form = ProductForm() 

    context = {
        'items': sorted_items, 
        'form': form,
        'workers_count': workers_count,
        'orders_count': orders_count,
        'notifications_count': notification_count,
        'products_count': products_count,
        'sort_option': sort_option, 
    }

    return render(request, 'dashboard/product.html', context)

#CRUD-Delete
@login_required
def product_delete(request, pk):
    item = Product.objects.get(id=pk)
    if request.method=='POST':
        item.delete()
        return redirect('dashboard-product')
    return render(request, 'dashboard/product_delete.html')

#CRUD- Update
@login_required
def product_update(request, pk):
    item = Product.objects.get(id=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            updated_product= form.save()
            if updated_product.quantity < 10:
                # Get the superuser's email (admin user)
                admin_emails = User.objects.filter(is_superuser=True).values_list('email', flat=True)
                if admin_emails:
                    send_mail(
                        'Low Stock Alert',
                        f'The product "{updated_product.name}" has low stock! Only {updated_product.quantity} remaining.',
                        settings.EMAIL_HOST_USER,  # your email
                        list(admin_emails),  # Admin's email
                        fail_silently=False,
                    )
            return redirect('dashboard-product')
    else:
        form = ProductForm(instance=item)
    context= {
        'form':form,
    }
    return render(request, 'dashboard/product_update.html', context)

@login_required
def order(request):
    orders = Order.objects.all()

    sort_option = request.GET.get('sort', 'date') 

    if sort_option == 'quantity':
        key = 'order_quantity'  
    else:  
        key = 'date' 

    orders_list = list(orders)

    orders_list = merge_sort(orders_list, key)

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')
        order = Order.objects.get(id=order_id)
        order.status = status
        order.save()
        return redirect('dashboard-order') 

    # Counts for the dashboard
    orders_count = orders.count()
    workers_count = User.objects.all().count()
    products_count = Product.objects.all().count()
    notification_count = Notification.objects.filter(is_read=0).count()

    context = {
        'orders': orders_list,  
        'workers_count': workers_count,
        'orders_count': orders_count,
        'products_count': products_count,
        'notifications_count': notification_count,
        'sort_option': sort_option 
    }

    return render(request, 'dashboard/order.html', context)

def notifications_view(request):
    notifications = Notification.objects.filter(is_read=False)
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})

def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.save()
    return redirect('dashboard-notifications')

def predict_demand(request, pk):
    # Load the trained model
    model = joblib.load('demand_prediction_model.pkl')

    # Get the product details
    product = Product.objects.get(pk=pk)

    # Prepare future dates for prediction (next month)
    future_dates = [datetime.now() + timedelta(days=i) for i in range(30)]
    future_month_index = [(date - datetime.now()).days / 30 for date in future_dates]

    # Make predictions using the model
    predictions = model.predict(np.array(future_month_index).reshape(-1, 1))

    # Get the predicted demand for the next month
    predicted_demand = predictions[-1]  # Last prediction (next month's prediction)

    # Render the prediction result in the template
    return render(request, 'dashboard/predict_demand.html', {
        'product': product,
        'prediction': predicted_demand,
    })
