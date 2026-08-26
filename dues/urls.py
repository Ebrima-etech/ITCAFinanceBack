from django.urls import path
from .views import MembershipDueListCreateView, MembershipDueDetailView

urlpatterns = [
    path('', MembershipDueListCreateView.as_view()),
    path('/<uuid:pk>', MembershipDueDetailView.as_view()),
]
