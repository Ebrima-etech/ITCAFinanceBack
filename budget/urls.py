from django.urls import path
from .views import BudgetListCreateView, BudgetDetailView

urlpatterns = [
    path('', BudgetListCreateView.as_view()),
    path('/<uuid:pk>', BudgetDetailView.as_view()),
]
