from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from customers.tasks import load_customer_data
from .serializers import CustomerSerializer
import math
import os
import tempfile


class RegisterCustomerView(APIView):
    def post(self, request):
        data = request.data
        monthly_income = data.get('monthly_income')

        approved_limit = int(round((36 * monthly_income) / 100000.0)) * 100000  # Round to nearest lakh

        customer = Customer.objects.create(
            first_name=data.get('First Name'),
            last_name=data.get('Last Name'),
            age=data.get('Age'),
            phone_number=data.get('Phone Number'),
            monthly_salary=monthly_income,
            approved_limit=approved_limit,
            current_debt=0,
        )

        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class UploadCustomerExcel(APIView):
    def post(self, request):
        excel_file = request.FILES.get('file')

        if not excel_file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        if not excel_file.name.endswith(('.xlsx', '.xls')):
            return Response({"error": "Invalid file format."}, status=status.HTTP_400_BAD_REQUEST)

        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            for chunk in excel_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        # Trigger Celery task
        load_customer_data.delay(tmp_path)

        return Response({"message": "Customer data is being processed in the background."}, status=status.HTTP_202_ACCEPTED)