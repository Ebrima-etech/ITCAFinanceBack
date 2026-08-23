from django.urls import path
from .views import TransactionListCreateView, TransactionDetailView

urlpatterns = [
    path('', TransactionListCreateView.as_view()),
    path('/<uuid:pk>', TransactionDetailView.as_view()),
]
