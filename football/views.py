from django.shortcuts import render
from rest_framework import serializers, generics, filters
from .models import Team, Player, Match, Appearance
from .serializers import (
    TeamSerializer,
    PlayerSerializer,
    MatchSerializer,
    MatchDetailSerializer,
)
from django.db.models import Sum, Q
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes


class TopScorerSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    player_name = serializers.CharField()
    team = serializers.CharField()
    total_goals = serializers.IntegerField()
    season = serializers.IntegerField()


class TopAssistSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    player_name = serializers.CharField()
    team = serializers.CharField()
    total_assists = serializers.IntegerField()
    season = serializers.IntegerField()


class MostMinutesSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    player_name = serializers.CharField()
    team = serializers.CharField()
    total_minutes = serializers.IntegerField()
    season = serializers.IntegerField()


class TeamTopScorerSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    player_name = serializers.CharField()
    team = serializers.CharField()
    total_goals = serializers.IntegerField()
    season = serializers.IntegerField()


class AppearanceSummarySerializer(serializers.Serializer):
    match_id = serializers.IntegerField()
    season = serializers.IntegerField()
    match_date = serializers.DateField()
    home_team = serializers.CharField()
    away_team = serializers.CharField()
    team = serializers.CharField()
    goals = serializers.IntegerField()
    assists = serializers.IntegerField()
    minutes_played = serializers.IntegerField()


class TeamStandingSerializer(serializers.Serializer):
    position = serializers.IntegerField()
    team_id = serializers.IntegerField()
    team = serializers.CharField()
    played = serializers.IntegerField()
    wins = serializers.IntegerField()
    draws = serializers.IntegerField()
    losses = serializers.IntegerField()
    goals_for = serializers.IntegerField()
    goals_against = serializers.IntegerField()
    goal_difference = serializers.IntegerField()
    points = serializers.IntegerField()
    season = serializers.IntegerField()




@extend_schema(tags=["Teams"], summary="List all teams")
class TeamListView(generics.ListAPIView):
    queryset = Team.objects.all().order_by("name")
    serializer_class = TeamSerializer


@extend_schema(tags=["Teams"], summary="Retrieve team details")
class TeamDetailView(generics.RetrieveAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


@extend_schema(
    tags=["Players"],
    summary="List all players",
    parameters=[
        OpenApiParameter(
            name="team_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter players by current team ID",
        ),
        OpenApiParameter(
            name="position",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter players by position (Attack, Midfield, Defender, Goalkeeper)",
        ),
        OpenApiParameter(
            name="nationality",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter players by nationality",
        ),
        OpenApiParameter(
            name="name",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Search players by name or full name",
        ),
    ],
)
class PlayerListView(generics.ListAPIView):
    serializer_class = PlayerSerializer

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["name", "nationality", "position", "height_cm", "market_value"]
    ordering = ["name"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="team_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter players by team id",
            ),
            OpenApiParameter(
                name="position",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter players by position",
            ),
            OpenApiParameter(
                name="nationality",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter players by nationality",
            ),
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Search players by name",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Order by one of: name, nationality, position, height_cm, market_value. Prefix with '-' for descending.",
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # queryset = Player.objects.select_related("current_team").all().order_by("name")
        queryset = Player.objects.select_related("current_team").all()

        team_id = self.request.query_params.get("team_id")
        position = self.request.query_params.get("position")
        nationality = self.request.query_params.get("nationality")
        name = self.request.query_params.get("name")

        if team_id:
            queryset = queryset.filter(current_team_id=team_id)

        if position:
            queryset = queryset.filter(position__icontains=position)

        if nationality:
            queryset = queryset.filter(nationality__icontains=nationality)
        
        if name:
            queryset = queryset.filter(
                Q(name__icontains=name) | Q(full_name__icontains=name)
            )

        return queryset


@extend_schema(tags=["Players"], summary="Retrieve player details")
class PlayerDetailView(generics.RetrieveAPIView):
    queryset = Player.objects.select_related("current_team").all()
    serializer_class = PlayerSerializer


@extend_schema(
    tags=["Matches"],
    summary="List all matches",
    parameters=[
        OpenApiParameter(
            name="season",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter matches by season year",
        ),
        OpenApiParameter(
            name="team_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter matches by team ID",
        ),
    ],
)
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


@extend_schema(tags=["Matches"], summary="Retrieve match details")
class MatchDetailView(generics.RetrieveAPIView):
    queryset = Match.objects.select_related("home_team", "away_team").prefetch_related("appearances")
    serializer_class = MatchDetailSerializer


@extend_schema(
    tags=["Analytics"],
    summary="Get top scorers",
    parameters=[
        OpenApiParameter(
            name="season",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Season year, e.g. 2023",
        ),
        OpenApiParameter(
            name="limit",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Number of results to return",
        ),
    ],
    responses={200: TopScorerSerializer(many=True)},
)
class TopScorersView(APIView):

    def get(self, request):

        season = request.query_params.get("season")
        limit = int(request.query_params.get("limit", 10))

        queryset = Appearance.objects.select_related("match")

        if season:
            queryset = queryset.filter(match__season=season)
            selected_season = int(season)
        else:
            selected_season = (
                queryset.values_list("match__season", flat=True)
                .order_by("-match__season")
                .first()
            )
            queryset = queryset.filter(match__season=selected_season)

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
                "season": selected_season,
            })

        return Response(results)



@extend_schema(
    tags=["Analytics"],
    summary="Get top assists",
    parameters=[
        OpenApiParameter(
            name="season",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Season year, e.g. 2023",
        ),
        OpenApiParameter(
            name="limit",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Number of results to return",
        ),
    ],
    responses={200: TopAssistSerializer(many=True)},
)
class TopAssistsView(APIView):

    def get(self, request):

        season = request.query_params.get("season")
        limit = int(request.query_params.get("limit", 10))

        queryset = Appearance.objects.select_related("match")

        if season:
            queryset = queryset.filter(match__season=season)
            selected_season = int(season)
        else:
            selected_season = (
                queryset.values_list("match__season", flat=True)
                .order_by("-match__season")
                .first()
            )
            queryset = queryset.filter(match__season=selected_season)

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
                "season": selected_season,
            })

        return Response(results)
    


@extend_schema(
    tags=["Analytics"],
    summary="Get players with most minutes played",
    parameters=[
        OpenApiParameter(
            name="season",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Season year, e.g. 2023",
        ),
        OpenApiParameter(
            name="limit",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Number of results to return",
        ),
    ],
    responses={200: MostMinutesSerializer(many=True)},
)
class MostMinutesView(APIView):

    def get(self, request):

        season = request.query_params.get("season")
        limit = int(request.query_params.get("limit", 10))

        queryset = Appearance.objects.select_related("match")

        if season:
            queryset = queryset.filter(match__season=season)
            selected_season = int(season)
        else:
            selected_season = (
                queryset.values_list("match__season", flat=True)
                .order_by("-match__season")
                .first()
            )
            queryset = queryset.filter(match__season=selected_season)

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
                "season": selected_season,
            })

        return Response(results)



@extend_schema(tags=["Teams"], summary="List players in a team")
class TeamPlayersView(ListAPIView):
    serializer_class = PlayerSerializer

    def get_queryset(self):
        team_id = self.kwargs["pk"]
        return Player.objects.select_related("current_team").filter(current_team_id=team_id).order_by("name")


@extend_schema(tags=["Players"], summary="List matches played by a player")
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


@extend_schema(
    tags=["Analytics"],
    summary="Get top scorers for a team",
    parameters=[
        OpenApiParameter(
            name="season",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Season year, e.g. 2023",
        ),
        OpenApiParameter(
            name="limit",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Number of results to return",
        ),
    ],
    responses={200: TeamTopScorerSerializer(many=True)},
)
class TeamTopScorersView(APIView):
    def get(self, request, pk):
        season = request.query_params.get("season")
        limit = int(request.query_params.get("limit", 5))

        queryset = Appearance.objects.filter(team_id=pk)

        if season:
            queryset = queryset.filter(match__season=season)
            selected_season = int(season)
        else:
            selected_season = (
                queryset.values_list("match__season", flat=True)
                .order_by("-match__season")
                .first()
            )
            queryset = queryset.filter(match__season=selected_season)

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
                "season": season if season else selected_season,
            })

        return Response(results)



@extend_schema(
    tags=["Teams"],
    summary="List matches for a team",
    parameters=[
        OpenApiParameter(
            name="season",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter matches by season year",
        ),
    ],
)
class TeamMatchesView(ListAPIView):
    serializer_class = MatchSerializer

    def get_queryset(self):
        team_id = self.kwargs["pk"]
        season = self.request.query_params.get("season")

        queryset = (
            Match.objects.select_related("home_team", "away_team")
            .filter(Q(home_team_id=team_id) | Q(away_team_id=team_id))
            .order_by("-match_date")
        )

        if season:
            queryset = queryset.filter(season=season)

        return queryset
    



@extend_schema(
    tags=["Players"],
    summary="List appearances for a player",
    parameters=[
        OpenApiParameter(
            name="season",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter appearances by season year",
        ),
    ],
    responses={200: AppearanceSummarySerializer(many=True)},
)
class PlayerAppearancesView(APIView):
    def get(self, request, pk):
        season = request.query_params.get("season")

        queryset = (
            Appearance.objects.select_related("match", "team", "player", "match__home_team", "match__away_team")
            .filter(player_id=pk)
            .order_by("-match__match_date")
        )

        if season:
            queryset = queryset.filter(match__season=season)

        results = []
        for appearance in queryset:
            results.append({
                "match_id": appearance.match.id,
                "season": appearance.match.season,
                "match_date": appearance.match.match_date,
                "home_team": appearance.match.home_team.name,
                "away_team": appearance.match.away_team.name,
                "team": appearance.team.name,
                "goals": appearance.goals,
                "assists": appearance.assists,
                "minutes_played": appearance.minutes_played,
            })

        return Response(results)







# Making standings table!!

def get_match_scores(match):
    home_goals = getattr(match, "home_score", None)
    away_goals = getattr(match, "away_score", None)

    if home_goals is None:
        home_goals = getattr(match, "home_goals", None)
    if away_goals is None:
        away_goals = getattr(match, "away_goals", None)

    if home_goals is None or away_goals is None:
        raise AttributeError(
            "Match model must have either "
            "'home_score'/'away_score' or 'home_goals'/'away_goals'."
        )

    return home_goals, away_goals


@extend_schema(
    tags=["Analytics"],
    summary="Get Premier League standings for a season",
    parameters=[
        OpenApiParameter(
            name="season",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Season year, e.g. 2023. If omitted, latest season is used.",
        ),
    ],
    responses={200: TeamStandingSerializer(many=True)},
)
class PremierLeagueStandingsView(APIView):
    def get(self, request):
        season = request.query_params.get("season")

        queryset = Match.objects.select_related("home_team", "away_team").all()

        if season:
            selected_season = int(season)
            queryset = queryset.filter(season=selected_season)
        else:
            selected_season = (
                queryset.values_list("season", flat=True)
                .order_by("-season")
                .first()
            )
            queryset = queryset.filter(season=selected_season)

        table = {}

        def init_team(team):
            if team.id not in table:
                table[team.id] = {
                    "team_id": team.id,
                    "team": team.name,
                    "played": 0,
                    "wins": 0,
                    "draws": 0,
                    "losses": 0,
                    "goals_for": 0,
                    "goals_against": 0,
                    "goal_difference": 0,
                    "points": 0,
                    "season": selected_season,
                }

        for match in queryset:
            home_team = match.home_team
            away_team = match.away_team
            home_goals, away_goals = get_match_scores(match)

            init_team(home_team)
            init_team(away_team)

            # played
            table[home_team.id]["played"] += 1
            table[away_team.id]["played"] += 1

            # goals
            table[home_team.id]["goals_for"] += home_goals
            table[home_team.id]["goals_against"] += away_goals

            table[away_team.id]["goals_for"] += away_goals
            table[away_team.id]["goals_against"] += home_goals

            # result / points
            if home_goals > away_goals:
                table[home_team.id]["wins"] += 1
                table[home_team.id]["points"] += 3
                table[away_team.id]["losses"] += 1
            elif home_goals < away_goals:
                table[away_team.id]["wins"] += 1
                table[away_team.id]["points"] += 3
                table[home_team.id]["losses"] += 1
            else:
                table[home_team.id]["draws"] += 1
                table[away_team.id]["draws"] += 1
                table[home_team.id]["points"] += 1
                table[away_team.id]["points"] += 1

        standings = list(table.values())

        for row in standings:
            row["goal_difference"] = row["goals_for"] - row["goals_against"]

        standings.sort(
            key=lambda x: (
                -x["points"],
                -x["goal_difference"],
                -x["goals_for"],
                x["team"],
            )
        )

        for idx, row in enumerate(standings, start=1):
            row["position"] = idx

        return Response(standings[:20])