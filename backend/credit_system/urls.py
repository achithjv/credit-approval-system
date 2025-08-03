from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def root_view(request):
    return JsonResponse({"message": "Welcome to the Credit Approval System API"})

urlpatterns = [
    path('', root_view),
    path('admin/', admin.site.urls),
    path('customers/', include('customers.urls')),
    path('loans/', include('loans.urls')),
]

