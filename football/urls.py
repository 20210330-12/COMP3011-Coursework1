from django.urls import path
from .views import (
    TeamListView,
    TeamDetailView,
    PlayerListView,
    PlayerDetailView,
    MatchListView,
    MatchDetailView,
    TopScorersView,
    TopAssistsView,
    MostMinutesView,
)

urlpatterns = [
    path("teams/", TeamListView.as_view(), name="team-list"),
    path("teams/<int:pk>/", TeamDetailView.as_view(), name="team-detail"),

    path("players/", PlayerListView.as_view(), name="player-list"),
    path("players/<int:pk>/", PlayerDetailView.as_view(), name="player-detail"),

    path("matches/", MatchListView.as_view(), name="match-list"),
    path("matches/<int:pk>/", MatchDetailView.as_view(), name="match-detail"),

    path("analytics/top-scorers/", TopScorersView.as_view()),
    path("analytics/top-assists/", TopAssistsView.as_view()),
    path("analytics/most-minutes/", MostMinutesView.as_view()),
]