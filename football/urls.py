from django.urls import path
from django.urls import path
from .views import (
    TeamListView,
    TeamDetailView,
    PlayerListView,
    PlayerDetailView,
    MatchListView,
    MatchDetailView,
    TeamPlayersView,
    TeamMatchesView,
    PlayerMatchesView,
    PlayerAppearancesView,
    TopScorersView,
    TopAssistsView,
    MostMinutesView,
    TeamTopScorersView,
    PremierLeagueStandingsView,
)

urlpatterns = [
    path("teams/", TeamListView.as_view(), name="team-list"),
    path("teams/<int:pk>/", TeamDetailView.as_view(), name="team-detail"),
    path("teams/<int:pk>/players/", TeamPlayersView.as_view(), name="team-players"),
    path("teams/<int:pk>/matches/", TeamMatchesView.as_view(), name="team-matches"),

    path("players/", PlayerListView.as_view(), name="player-list"),
    path("players/<int:pk>/", PlayerDetailView.as_view(), name="player-detail"),
    path("players/<int:pk>/matches/", PlayerMatchesView.as_view(), name="player-matches"),
    path("players/<int:pk>/appearances/", PlayerAppearancesView.as_view(), name="player-appearances"),

    path("matches/", MatchListView.as_view(), name="match-list"),
    path("matches/<int:pk>/", MatchDetailView.as_view(), name="match-detail"),

    path("analytics/top-scorers/", TopScorersView.as_view(), name="top-scorers"),
    path("analytics/top-assists/", TopAssistsView.as_view(), name="top-assists"),
    path("analytics/most-minutes/", MostMinutesView.as_view(), name="most-minutes"),
    path("analytics/standings/", PremierLeagueStandingsView.as_view(), name="premier-league-standings"),
    path("teams/<int:pk>/top-scorers/", TeamTopScorersView.as_view(), name="team-top-scorers"),
]