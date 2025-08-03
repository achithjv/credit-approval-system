from django.urls import path
from .views import RegisterCustomerView
from customers.views import UploadCustomerExcel


urlpatterns = [
    path('register/', RegisterCustomerView.as_view(), name='register'),
    path('import/customers/', UploadCustomerExcel.as_view(), name='import-customers'),
]

