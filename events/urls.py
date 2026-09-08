from django.urls import path
from .views import (
    EventListCreateView, EventDetailView, EventImportRevenueView,
    EventPartnerListCreateView, EventPartnerDetailView, AllEventPartnersListView,
)

urlpatterns = [
    path('', EventListCreateView.as_view()),
    path('partners/', AllEventPartnersListView.as_view()),
    path('<uuid:pk>/import-revenue/', EventImportRevenueView.as_view()),
    path('<uuid:pk>/partners/', EventPartnerListCreateView.as_view()),
    path('<uuid:pk>/partners/<uuid:partner_id>/', EventPartnerDetailView.as_view()),
    path('<uuid:pk>/', EventDetailView.as_view()),
]
