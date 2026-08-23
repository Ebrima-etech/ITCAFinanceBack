from rest_framework import generics
from rest_framework.response import Response
from activitylog.utils import record_activity
from .models import User
from .permissions import IsAdmin
from .serializers import UserSerializer, CreateUserSerializer, UpdateUserSerializer


# Admin-only: create and deactivate officer accounts as the committee
# turns over, so a new finance officer gets clean access on day one.
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by('created_at')
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        return CreateUserSerializer if self.request.method == 'POST' else UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        record_activity(
            action='CREATE',
            entity_type='User',
            entity_id=str(user.id),
            actor=self.request.user,
            details={'name': user.name, 'email': user.email, 'role': user.role},
        )


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer
    permission_classes = [IsAdmin]

    def perform_update(self, serializer):
        user = serializer.save()
        record_activity(
            action='UPDATE',
            entity_type='User',
            entity_id=str(user.id),
            actor=self.request.user,
            details={'changed': list(self.request.data.keys())},
        )

    # Accounts are deactivated, never hard-deleted, so past activity-log
    # entries referencing this user stay meaningful.
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=['is_active'])
        record_activity(action='DEACTIVATE', entity_type='User', entity_id=str(user.id), actor=request.user)
        return Response(UserSerializer(user).data)
