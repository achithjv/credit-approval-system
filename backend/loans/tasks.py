from celery import shared_task
import pandas as pd
from .models import Loan
from customers.models import Customer
from datetime import datetime

@shared_task
def load_loan_data(file_path):
    df = pd.read_excel(file_path)

    for _, row in df.iterrows():
        customer = Customer.objects.get(id=row['Customer ID'])

        Loan.objects.update_or_create(
            id=row['Loan ID'],
            defaults={
                'customer': customer,
                'loan_amount': row['Loan Amount'],
                'interest_rate': row['Interest Rate'],
                'tenure': row['Tenure'],
                'monthly_installment': row['Monthly payment'],
                'emis_paid_on_time': row['EMIs paid on Time'],
                'start_date': row['Date of Approval'].date(),
                'end_date': row['End Date'].date()

            }
        )
    return f"{len(df)} loans loaded successfully."
