from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from accounts.models import User


# Phase 0 proof: one route that talks to the database, so the frontend has
# something real to fetch while confirming the skeleton is alive.
def health(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'ITCA Finance API is running',
        'userCount': User.objects.count(),
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health', health),
    path('api/auth/', include('accounts.auth_urls')),
    path('api/users', include('accounts.urls')),
    path('api/activity-log', include('activitylog.urls')),
    path('api/transactions', include('ledger.urls')),
    path('api/events', include('events.urls')),
    path('api/membership-dues', include('dues.urls')),
    path('api/budget', include('budget.urls')),
    path('api/dashboard', include('dashboard.urls')),
    path('api/reports/', include('reports.urls')),
]
