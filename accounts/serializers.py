from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    display_name = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ["username", "email", "password", "display_name"]

    def create(self, validated_data):
        display_name = validated_data.pop("display_name")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"]
        )

        UserProfile.objects.create(
            user=user,
            display_name=display_name
        )

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    favourite_team_name = serializers.CharField(source="favourite_team.name", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "display_name",
            "bio",
            "favourite_team",
            "favourite_team_name",
            "created_at",
            "updated_at",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile"]