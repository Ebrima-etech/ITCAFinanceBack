from django.urls import path
from .auth_views import LoginView, MeView

urlpatterns = [
    path('login', LoginView.as_view()),
    path('me', MeView.as_view()),
]
