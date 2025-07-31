from django.conf import settings
from django.contrib.auth import logout
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializers import LoginSerializer, RegisterSerializer
from users.tasks import send_registration_email
from rest_framework.request import Request


class RegisterApiView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def post(self, request: Request, *args, **kwargs) -> Response:
        user = super().post(request, *args, **kwargs)
        user_email = user.data["email"]
        if settings.CELERY_RUN:
            send_registration_email.delay(user_email)
        return Response(user.data, status=status.HTTP_201_CREATED)


class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    queryset = User.objects.all()

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request) -> Response:
        logout(request)
        return Response({"success": "Successfully logged out"}, status=status.HTTP_200_OK)
