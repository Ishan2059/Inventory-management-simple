from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
import csv
from .models import Product, Notification
import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

@receiver(post_save, sender=Product)
def create_low_stock_notification(sender, instance, **kwargs):
    if instance.is_below_threshold():
        Notification.objects.get_or_create(
            product=instance,
            message=f"Low stock alert: {instance.name} has only {instance.quantity} left."
        )

@receiver(post_save, sender=Product)
def update_product_csv(sender, instance, created, **kwargs):
    if created:
        # Add the new product to the CSV file
        with open('product_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                instance.id,
                instance.name,
                instance.quantity,
                instance.category,
                instance.price_each,
                instance.supplier,
                instance.date,
            ])
        
        # Retrain the model with the updated product data
        df = pd.read_csv('product_data.csv')
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        monthly_data = df.groupby('month').agg({'quantity': 'sum'}).reset_index()
        monthly_data['month_index'] = (monthly_data['month'].dt.start_time - monthly_data['month'].dt.start_time.min()) / pd.Timedelta(days=30)

        X = monthly_data[['month_index']]
        y = monthly_data['quantity']
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Save the updated model
        joblib.dump(model, 'demand_prediction_model.pkl')

        print("Model retrained and saved after adding new product")

def retrain_model():
    # Fetch all product data from the database
    products = Product.objects.all()
    
    # Create a DataFrame from the database query
    data = []
    for product in products:
        data.append({
            'id': product.id,
            'name': product.name,
            'quantity': product.quantity,
            'date': product.date,
        })
    
    df = pd.DataFrame(data)
    
    # Convert 'date' to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Aggregate the data by month to calculate the total quantity demand per month
    df['month'] = df['date'].dt.to_period('M')
    monthly_data = df.groupby('month').agg({'quantity': 'sum'}).reset_index()

    # Prepare the data for training
    monthly_data['month_index'] = (monthly_data['month'].dt.start_time - monthly_data['month'].dt.start_time.min()) / pd.Timedelta(days=30)
    X = monthly_data[['month_index']]  # Feature: Month index
    y = monthly_data['quantity']      # Target: Total quantity demand for the month

    # Initialize the model (Linear Regression)
    model = LinearRegression()

    # Train the model
    model.fit(X, y)

    # Save the trained model as a .pkl file
    joblib.dump(model, 'demand_prediction_model.pkl')

@receiver(post_save, sender=Product)
def update_model_on_save(sender, instance, created, **kwargs):
    retrain_model()

# Signal handler for when a product is deleted
@receiver(post_delete, sender=Product)
def update_model_on_delete(sender, instance, **kwargs):
    retrain_model()