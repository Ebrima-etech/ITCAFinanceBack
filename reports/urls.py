from django.urls import path
from .views import TransactionsReportView

urlpatterns = [
    path('transactions', TransactionsReportView.as_view()),
]
