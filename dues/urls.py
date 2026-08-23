from django.urls import path
from .views import MembershipDueListCreateView

urlpatterns = [
    path('', MembershipDueListCreateView.as_view()),
]
