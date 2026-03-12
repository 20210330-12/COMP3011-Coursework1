from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserSerializer
from drf_spectacular.utils import extend_schema


class RegisterRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    display_name = serializers.CharField()
    bio = serializers.CharField(required=False, allow_blank=True)
    favourite_team = serializers.IntegerField(required=False, allow_null=True)


class UserProfileResponseSerializer(serializers.Serializer):
    display_name = serializers.CharField()
    bio = serializers.CharField(allow_blank=True, required=False)
    favourite_team = serializers.IntegerField(allow_null=True, required=False)
    favourite_team_name = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class UserResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    profile = UserProfileResponseSerializer()


class AuthSuccessSerializer(serializers.Serializer):
    message = serializers.CharField()
    token = serializers.CharField()
    user = UserResponseSerializer()


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()


class MeResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField(allow_blank=True, required=False)
    profile = UserProfileResponseSerializer()


@extend_schema(
    request=RegisterRequestSerializer,
    responses={201: AuthSuccessSerializer, 400: ErrorSerializer},
    tags=["Authentication"],
    summary="Register a new user",
)
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "message": "User registered successfully",
                    "token": token.key,
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=LoginRequestSerializer,
    responses={200: AuthSuccessSerializer, 400: ErrorSerializer, 401: ErrorSerializer},
    tags=["Authentication"],
    summary="Login and get auth token",
)
class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "message": "Login successful",
                "token": token.key,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK
        )


@extend_schema(
    responses={200: MeResponseSerializer},
    tags=["Authentication"],
    summary="Get current authenticated user",
)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=None,
    responses={200: MessageSerializer, 401: ErrorSerializer},
    tags=["Authentication"],
    summary="Logout current user",
    description="Deletes the current user's authentication token.",
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK
        )


@extend_schema(
    request=None,
    responses={200: MessageSerializer, 401: ErrorSerializer},
    tags=["Authentication"],
    summary="Delete current user account",
    description="Deletes the authenticated user's account and profile.",
)
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(
            {"message": "Account deleted successfully"},
            status=status.HTTP_200_OK
        )