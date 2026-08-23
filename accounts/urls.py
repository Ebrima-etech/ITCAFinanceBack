from django.urls import path
from .views import UserListCreateView, UserDetailView

urlpatterns = [
    path('', UserListCreateView.as_view()),
    path('/<uuid:pk>', UserDetailView.as_view()),
]
