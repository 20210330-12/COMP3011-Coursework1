# football/serializers.py
from rest_framework import serializers
from .models import Team, Player, Match, Appearance


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            "id",
            "external_id",
            "name",
            "short_name",
            "country",
            "competition",
            "season",
            "stadium",
            "founded",
            "logo_url",
            "created_at",
            "updated_at",
        ]


class PlayerSerializer(serializers.ModelSerializer):
    current_team_name = serializers.CharField(source="current_team.name", read_only=True)

    class Meta:
        model = Player
        fields = [
            "id",
            "external_id",
            "name",
            "full_name",
            "date_of_birth",
            "nationality",
            "position",
            "current_team",
            "current_team_name",
            "market_value",
            "height_cm",
            "preferred_foot",
            "image_url",
            "created_at",
            "updated_at",
        ]


class AppearanceSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source="player.name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = Appearance
        fields = [
            "id",
            "player",
            "player_name",
            "team",
            "team_name",
            "minutes_played",
            "goals",
            "assists",
            "yellow_cards",
            "red_cards",
            "position_played",
            "rating",
            "is_starter",
            "appearance_date",
        ]


class MatchSerializer(serializers.ModelSerializer):
    home_team_name = serializers.CharField(source="home_team.name", read_only=True)
    away_team_name = serializers.CharField(source="away_team.name", read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "external_id",
            "competition",
            "season",
            "match_date",
            "home_team",
            "home_team_name",
            "away_team",
            "away_team_name",
            "home_score",
            "away_score",
            "venue",
            "attendance",
            "created_at",
            "updated_at",
        ]


class MatchDetailSerializer(serializers.ModelSerializer):
    home_team_name = serializers.CharField(source="home_team.name", read_only=True)
    away_team_name = serializers.CharField(source="away_team.name", read_only=True)
    appearances = AppearanceSerializer(many=True, read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "external_id",
            "competition",
            "season",
            "match_date",
            "home_team",
            "home_team_name",
            "away_team",
            "away_team_name",
            "home_score",
            "away_score",
            "venue",
            "attendance",
            "appearances",
            "created_at",
            "updated_at",
        ]