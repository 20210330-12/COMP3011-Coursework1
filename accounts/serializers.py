from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile
from football.models import Team


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    display_name = serializers.CharField(max_length=100)
    bio = serializers.CharField(required=False, allow_blank=True)
    favourite_team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "display_name", "bio", "favourite_team"]

    def create(self, validated_data):
        display_name = validated_data.pop("display_name")
        bio = validated_data.pop("bio", "")
        favourite_team = validated_data.pop("favourite_team", None)

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"]
        )

        UserProfile.objects.create(
            user=user,
            display_name=display_name,
            bio=bio,
            favourite_team=favourite_team,
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