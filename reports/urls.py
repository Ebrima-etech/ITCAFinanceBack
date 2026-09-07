from django.urls import path
from .views import TransactionsReportView, PublicFinancialReportView

urlpatterns = [
    path('transactions', TransactionsReportView.as_view()),
    path('public', PublicFinancialReportView.as_view()),
]
