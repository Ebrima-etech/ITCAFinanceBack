from rest_framework.generics import ListAPIView
from accounts.permissions import IsAdmin
from .models import ActivityLog
from .serializers import ActivityLogSerializer


class ActivityLogListView(ListAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = ActivityLog.objects.select_related('actor').all()
        entity_type = self.request.query_params.get('entityType')
        if entity_type:
            qs = qs.filter(entity_type=entity_type)
        take = int(self.request.query_params.get('take', 100))
        return qs[:take]
