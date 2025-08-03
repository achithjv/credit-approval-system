from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from datetime import datetime, timedelta
from .serializers import (
    LoanEligibilityRequestSerializer,
    CreateLoanSerializer,
    LoanDetailSerializer
)
from customers.models import Customer
from loans.models import Loan
from loans.tasks import load_loan_data
import tempfile


class CheckLoanEligibilityView(APIView):
    def post(self, request):
        serializer = LoanEligibilityRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        customer_id = data['customer_id']
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        tenure = data['tenure']

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=404)

        loans = Loan.objects.filter(customer=customer)

        if customer.current_debt > customer.approved_limit:
            credit_score = 0
        else:
            on_time_loan_count = sum([loan.emis_paid_on_time for loan in loans])
            total_loans = loans.count()
            current_year_loans = loans.filter(start_date__year=datetime.now().year).count()
            total_loan_volume = sum([loan.loan_amount for loan in loans])

            credit_score = 0
            credit_score += min((on_time_loan_count / total_loans) * 40 if total_loans else 40, 40)
            credit_score += max(0, 20 - total_loans)
            credit_score += min(current_year_loans * 5, 20)
            credit_score += min(total_loan_volume / 100000, 20)

        # EMI calculation
        r = interest_rate / (12 * 100)
        emi = (loan_amount * r * ((1 + r) ** tenure)) / (((1 + r) ** tenure) - 1)

        if emi > (customer.monthly_salary * 0.5):
            return Response({
                "customer_id": customer_id,
                "approval": False,
                "interest_rate": interest_rate,
                "corrected_interest_rate": interest_rate,
                "tenure": tenure,
                "monthly_installment": round(emi, 2)
            }, status=200)

        approval = True
        corrected_interest_rate = interest_rate

        if credit_score < 10:
            approval = False
        elif credit_score < 30 and interest_rate < 16:
            corrected_interest_rate = 16.0
        elif credit_score < 50 and interest_rate < 12:
            corrected_interest_rate = 12.0

        response = {
            "customer_id": customer_id,
            "approval": approval,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": tenure,
            "monthly_installment": round(emi, 2)
        }

        return Response(response, status=200)


class CreateLoanView(APIView):
    def post(self, request):
        data = request.data
        customer_id = data.get('customer_id')
        loan_amount = data.get('loan_amount')
        interest_rate = data.get('interest_rate')
        tenure = data.get('tenure')

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=404)

        r = interest_rate / (12 * 100)
        emi = (loan_amount * r * ((1 + r) ** tenure)) / (((1 + r) ** tenure) - 1)

        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=30 * tenure)

        loan = Loan.objects.create(
            customer=customer,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure=tenure,
            monthly_installment=emi,
            emis_paid_on_time=0,
            start_date=start_date,
            end_date=end_date
        )

        customer.current_debt += loan_amount
        customer.save()

        serializer = CreateLoanSerializer(loan)
        return Response(serializer.data, status=201)


class ViewLoanByIDView(RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanDetailSerializer
    lookup_field = 'id'


class ViewLoansByCustomerView(ListAPIView):
    serializer_class = LoanDetailSerializer

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return Loan.objects.filter(customer__id=customer_id)


class UploadLoanExcel(APIView):
    def post(self, request):
        excel_file = request.FILES.get('file')

        if not excel_file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        if not excel_file.name.endswith(('.xlsx', '.xls')):
            return Response({"error": "Invalid file format."}, status=status.HTTP_400_BAD_REQUEST)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            for chunk in excel_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        load_loan_data.delay(tmp_path)

        return Response(
            {"message": "Loan data is being processed in the background."},
            status=status.HTTP_202_ACCEPTED
        )
