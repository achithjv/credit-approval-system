from django.urls import path
from .views import (
    CheckLoanEligibilityView,
    CreateLoanView,
    ViewLoanByIDView,
    ViewLoansByCustomerView,
    UploadLoanExcel,  # ✅ Import the new view
)

urlpatterns = [
    path('check-eligibility/', CheckLoanEligibilityView.as_view(), name='check_eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create_loan'),
    path('view-loan/<int:id>/', ViewLoanByIDView.as_view(), name='view_loan_by_id'),
    path('view-loans/<int:customer_id>/', ViewLoansByCustomerView.as_view(), name='view_loans_by_customer'),
    
    # ✅ New upload endpoint
    path('import/loans/', UploadLoanExcel.as_view(), name='import_loans'),
]
