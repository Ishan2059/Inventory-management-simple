import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
from django.core.management.base import BaseCommand
from dashboard.models import Product  # Adjust this according to your app and model name

class Command(BaseCommand):
    help = 'Train the demand prediction model based on product data'

    def handle(self, *args, **kwargs):
        # Fetch product data from the database
        products = Product.objects.all()

        # Prepare the data
        product_data = []
        for product in products:
            product_data.append({
                'id': product.id,
                'name': product.name,
                'quantity': product.quantity,
                'date': product.date,
            })

        # Convert the product data into a DataFrame
        df = pd.DataFrame(product_data)

        # Convert 'date' to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Aggregate the data by month to calculate the total quantity demand per month
        df['month'] = df['date'].dt.to_period('M')
        monthly_data = df.groupby('month').agg({'quantity': 'sum'}).reset_index()

        # Prepare the data for training
        # Use the month index as the feature (e.g., 0, 1, 2, ...) and quantity as the target variable
        monthly_data['month_index'] = (monthly_data['month'].dt.start_time - monthly_data['month'].dt.start_time.min()) / pd.Timedelta(days=30)
        X = monthly_data[['month_index']]  # Feature: Month index
        y = monthly_data['quantity']      # Target: Total quantity demand for the month

        # Initialize the model (Linear Regression)
        model = LinearRegression()

        # Train the model
        model.fit(X, y)

        # Save the trained model as a .pkl file
        joblib.dump(model, 'demand_prediction_model.pkl')

        self.stdout.write(self.style.SUCCESS("Model trained and saved as demand_prediction_model.pkl"))
