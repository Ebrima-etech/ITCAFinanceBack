from django.urls import path
from .views import EventListCreateView, EventDetailView, EventImportRevenueView

urlpatterns = [
    path('', EventListCreateView.as_view()),
    path('/<uuid:pk>', EventDetailView.as_view()),
    path('/<uuid:pk>/import-revenue', EventImportRevenueView.as_view()),
]
