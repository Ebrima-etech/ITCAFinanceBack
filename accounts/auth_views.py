from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from activitylog.utils import record_activity
from .serializers import UserSerializer


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is None or not user.is_active:
            raise AuthenticationFailed('Invalid email or password')

        token = AccessToken.for_user(user)

        record_activity(action='LOGIN', entity_type='User', entity_id=str(user.id), actor=user)

        return Response({
            'access_token': str(token),
            'user': UserSerializer(user).data,
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
