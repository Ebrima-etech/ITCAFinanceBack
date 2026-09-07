from django.urls import path
from .views import (
    EventListCreateView, EventDetailView, EventImportRevenueView,
    EventPartnerListCreateView, EventPartnerDetailView,
)

urlpatterns = [
    path('', EventListCreateView.as_view()),
    path('/<uuid:pk>', EventDetailView.as_view()),
    path('/<uuid:pk>/import-revenue', EventImportRevenueView.as_view()),
    path('/<uuid:event_id>/partners', EventPartnerListCreateView.as_view()),
    path('/<uuid:event_id>/partners/<uuid:pk>', EventPartnerDetailView.as_view()),
]
