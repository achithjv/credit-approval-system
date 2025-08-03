from celery import shared_task
import pandas as pd
from customers.models import Customer
from loans.models import Loan
from datetime import datetime

@shared_task
def ingest_excel_data():
    customer_df = pd.read_excel('data_ingestion/data/customer_data.xlsx')
    loan_df = pd.read_excel('data_ingestion/data/loan_data.xlsx')

    for _, row in customer_df.iterrows():
        Customer.objects.update_or_create(
            phone_number=row['Phone Number'],
            defaults={
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'monthly_salary': row['Monthly Salary'],
                'approved_limit': row['Approved Limit'],
                'current_debt': row['Current Debt']
            }
        )

    for _, row in loan_df.iterrows():
        try:
            customer = Customer.objects.get(phone_number=row['Phone Number'])
            Loan.objects.update_or_create(
                customer=customer,
                loan_amount=row['Loan Amount'],
                interest_rate=row['Interest Rate'],
                tenure=row['Tenure'],
                defaults={
                    'emi': row['EMI'],
                    'emis_paid_on_time': row['EMIs Paid on Time'],
                    'start_date': datetime.strptime(row['Start Date'], '%Y-%m-%d'),
                    'end_date': datetime.strptime(row['End Date'], '%Y-%m-%d')
                }
            )
        except Customer.DoesNotExist:
            continue

    return "Excel Data Ingested Successfully"
