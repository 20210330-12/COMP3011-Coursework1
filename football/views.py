from django.shortcuts import render
from rest_framework import generics
from .models import Team, Player, Match, Appearance
from .serializers import (
    TeamSerializer,
    PlayerSerializer,
    MatchSerializer,
    MatchDetailSerializer,
)
from django.db.models import Sum
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response


class TeamListView(generics.ListAPIView):
    queryset = Team.objects.all().order_by("name")
    serializer_class = TeamSerializer


class TeamDetailView(generics.RetrieveAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class PlayerListView(generics.ListAPIView):
    serializer_class = PlayerSerializer

    def get_queryset(self):
        queryset = Player.objects.select_related("current_team").all().order_by("name")

        team_id = self.request.query_params.get("team_id")
        position = self.request.query_params.get("position")
        nationality = self.request.query_params.get("nationality")

        if team_id:
            queryset = queryset.filter(current_team_id=team_id)

        if position:
            queryset = queryset.filter(position__icontains=position)

        if nationality:
            queryset = queryset.filter(nationality__icontains=nationality)

        return queryset


class PlayerDetailView(generics.RetrieveAPIView):
    queryset = Player.objects.select_related("current_team").all()
    serializer_class = PlayerSerializer


class MatchListView(generics.ListAPIView):
    serializer_class = MatchSerializer

    def get_queryset(self):
        queryset = (
            Match.objects.select_related("home_team", "away_team")
            .all()
            .order_by("-match_date")
        )

        season = self.request.query_params.get("season")
        team_id = self.request.query_params.get("team_id")

        if season:
            queryset = queryset.filter(season=season)

        if team_id:
            queryset = queryset.filter(home_team_id=team_id) | queryset.filter(away_team_id=team_id)

        return queryset


class MatchDetailView(generics.RetrieveAPIView):
    queryset = Match.objects.select_related("home_team", "away_team").prefetch_related("appearances")
    serializer_class = MatchDetailSerializer


class TopScorersView(APIView):

    def get(self, request):

        season = request.query_params.get("season")
        limit = int(request.query_params.get("limit", 10))

        queryset = Appearance.objects.select_related("match")

        if season:
            queryset = queryset.filter(match__season=season)
        else:
            latest_season = (
                queryset.values_list("match__season", flat=True)
                .order_by("-match__season")
                .first()
            )
            queryset = queryset.filter(match__season=latest_season)

        data = (
            queryset
            .values("player__id", "player__name", "team__name")
            .annotate(total_goals=Sum("goals"))
            .order_by("-total_goals")[:limit]
        )

        results = []

        for row in data:
            results.append({
                "player_id": row["player__id"],
                "player_name": row["player__name"],
                "team": row["team__name"],
                "total_goals": row["total_goals"],
            })

        return Response(results)



class TopAssistsView(APIView):

    def get(self, request):

        season = request.query_params.get("season")
        limit = int(request.query_params.get("limit", 10))

        queryset = Appearance.objects.select_related("match")

        if season:
            queryset = queryset.filter(match__season=season)
        else:
            latest_season = (
                queryset.values_list("match__season", flat=True)
                .order_by("-match__season")
                .first()
            )
            queryset = queryset.filter(match__season=latest_season)

        data = (
            queryset
            .values("player__id", "player__name", "team__name")
            .annotate(total_assists=Sum("assists"))
            .order_by("-total_assists")[:limit]
        )

        results = []

        for row in data:
            results.append({
                "player_id": row["player__id"],
                "player_name": row["player__name"],
                "team": row["team__name"],
                "total_assists": row["total_assists"],
            })

        return Response(results)
    


class MostMinutesView(APIView):

    def get(self, request):

        season = request.query_params.get("season")
        limit = int(request.query_params.get("limit", 10))

        queryset = Appearance.objects.select_related("match")

        if season:
            queryset = queryset.filter(match__season=season)
        else:
            latest_season = (
                queryset.values_list("match__season", flat=True)
                .order_by("-match__season")
                .first()
            )
            queryset = queryset.filter(match__season=latest_season)

        data = (
            queryset
            .values("player__id", "player__name", "team__name")
            .annotate(total_minutes=Sum("minutes_played"))
            .order_by("-total_minutes")[:limit]
        )

        results = []

        for row in data:
            results.append({
                "player_id": row["player__id"],
                "player_name": row["player__name"],
                "team": row["team__name"],
                "total_minutes": row["total_minutes"],
            })

        return Response(results)



class TeamPlayersView(ListAPIView):
    serializer_class = PlayerSerializer

    def get_queryset(self):
        team_id = self.kwargs["pk"]
        return Player.objects.select_related("current_team").filter(current_team_id=team_id).order_by("name")


class PlayerMatchesView(ListAPIView):
    serializer_class = MatchSerializer

    def get_queryset(self):
        player_id = self.kwargs["pk"]

        match_ids = (
            Appearance.objects.filter(player_id=player_id)
            .values_list("match_id", flat=True)
            .distinct()
        )

        return (
            Match.objects.select_related("home_team", "away_team")
            .filter(id__in=match_ids)
            .order_by("-match_date")
        )


class TeamTopScorersView(APIView):
    def get(self, request, pk):
        season = request.query_params.get("season")
        limit = int(request.query_params.get("limit", 5))

        queryset = Appearance.objects.filter(team_id=pk)

        if season:
            queryset = queryset.filter(match__season=season)
        else:
            latest_season = (
                queryset.values_list("match__season", flat=True)
                .order_by("-match__season")
                .first()
            )
            queryset = queryset.filter(match__season=latest_season)

        data = (
            queryset.values("player__id", "player__name", "team__name")
            .annotate(total_goals=Sum("goals"))
            .order_by("-total_goals")[:limit]
        )

        results = []
        for row in data:
            results.append({
                "player_id": row["player__id"],
                "player_name": row["player__name"],
                "team": row["team__name"],
                "total_goals": row["total_goals"],
                "season": season if season else latest_season,
            })

        return Response(results)