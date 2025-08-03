from celery import shared_task
import pandas as pd
from .models import Customer
from loans.models import Loan

@shared_task
def load_customer_data(file_path):
    df = pd.read_excel(file_path)

    # Rename Excel columns to match model fields
    df.rename(columns={
        'Customer ID': 'customer_id',
        'First Name': 'first_name',
        'Last Name': 'last_name',
        'Phone Number': 'phone_number',
        'Age': 'age',
        'Monthly Salary': 'monthly_salary',
        'Approved Limit': 'approved_limit',
    }, inplace=True)

    for _, row in df.iterrows():
        Customer.objects.update_or_create(
            phone_number=row['phone_number'],
            defaults={
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'age': row['age'],
                'monthly_salary': row['monthly_salary'],
                'approved_limit': row['approved_limit'],
            }
        )
    return f"{len(df)} customers loaded successfully."


@shared_task
def load_loan_data(file_path):
    df = pd.read_excel(file_path)

    # Rename columns if necessary (based on Excel headers)
    df.rename(columns={
        'loan_id': 'loan_id',
        'customer_id': 'customer_id',
        'loan_amount': 'loan_amount',
        'tenure': 'tenure',
        'interest_rate': 'interest_rate',
        'monthly_payment': 'monthly_installment',
        'EMIs paid on time': 'emis_paid_on_time',
        'start_date': 'start_date',
        'end_date': 'end_date',
    }, inplace=True)

    for _, row in df.iterrows():
        Loan.objects.update_or_create(
            id=row['loan_id'],
            defaults={
                'customer_id': row['customer_id'],
                'loan_amount': row['loan_amount'],
                'tenure': row['tenure'],
                'interest_rate': row['interest_rate'],
                'monthly_installment': row['monthly_installment'],
                'emis_paid_on_time': row['emis_paid_on_time'],
                'start_date': pd.to_datetime(row['start_date']).date(),
                'end_date': pd.to_datetime(row['end_date']).date(),
            }
        )
    return f"{len(df)} loans loaded successfully."
