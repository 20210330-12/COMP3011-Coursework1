from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from football.models import Team, Player, Match, Appearance


class FootballAPITestCase(APITestCase):
    def setUp(self):
        self.arsenal = Team.objects.create(
            external_id="team-ars",
            name="Arsenal",
            short_name="ARS",
            country="England",
            competition="Premier League",
            season=2023,
            stadium="Emirates Stadium",
            founded=1886,
        )
        self.chelsea = Team.objects.create(
            external_id="team-che",
            name="Chelsea",
            short_name="CHE",
            country="England",
            competition="Premier League",
            season=2023,
            stadium="Stamford Bridge",
            founded=1905,
        )
        self.liverpool = Team.objects.create(
            external_id="team-liv",
            name="Liverpool",
            short_name="LIV",
            country="England",
            competition="Premier League",
            season=2023,
            stadium="Anfield",
            founded=1892,
        )

        self.saka = Player.objects.create(
            external_id="player-saka",
            name="Bukayo Saka",
            full_name="Bukayo Saka",
            nationality="England",
            position="Forward",
            current_team=self.arsenal,
            preferred_foot="Left",
            height_cm=178,
            market_value=100000000,
        )
        self.odegaard = Player.objects.create(
            external_id="player-odegaard",
            name="Martin Odegaard",
            full_name="Martin Odegaard",
            nationality="Norway",
            position="Midfielder",
            current_team=self.arsenal,
            preferred_foot="Left",
            height_cm=178,
            market_value=90000000,
        )
        self.palmer = Player.objects.create(
            external_id="player-palmer",
            name="Cole Palmer",
            full_name="Cole Palmer",
            nationality="England",
            position="Forward",
            current_team=self.chelsea,
            preferred_foot="Left",
            height_cm=189,
            market_value=80000000,
        )
        self.salah = Player.objects.create(
            external_id="player-salah",
            name="Mohamed Salah",
            full_name="Mohamed Salah",
            nationality="Egypt",
            position="Forward",
            current_team=self.liverpool,
            preferred_foot="Left",
            height_cm=175,
            market_value=75000000,
        )

        now = timezone.now()

        self.match_1 = Match.objects.create(
            external_id="match-1",
            competition="Premier League",
            season=2023,
            match_date=now - timedelta(days=10),
            home_team=self.arsenal,
            away_team=self.chelsea,
            home_score=2,
            away_score=1,
            venue="Emirates Stadium",
            attendance=60000,
        )
        self.match_2 = Match.objects.create(
            external_id="match-2",
            competition="Premier League",
            season=2023,
            match_date=now - timedelta(days=5),
            home_team=self.chelsea,
            away_team=self.liverpool,
            home_score=1,
            away_score=1,
            venue="Stamford Bridge",
            attendance=40000,
        )
        self.match_3 = Match.objects.create(
            external_id="match-3",
            competition="Premier League",
            season=2022,
            match_date=now - timedelta(days=370),
            home_team=self.arsenal,
            away_team=self.liverpool,
            home_score=3,
            away_score=0,
            venue="Emirates Stadium",
            attendance=59000,
        )

        Appearance.objects.create(
            player=self.saka,
            match=self.match_1,
            team=self.arsenal,
            minutes_played=90,
            goals=1,
            assists=1,
            is_starter=True,
            appearance_date=self.match_1.match_date.date(),
        )
        Appearance.objects.create(
            player=self.odegaard,
            match=self.match_1,
            team=self.arsenal,
            minutes_played=90,
            goals=1,
            assists=0,
            is_starter=True,
            appearance_date=self.match_1.match_date.date(),
        )
        Appearance.objects.create(
            player=self.palmer,
            match=self.match_1,
            team=self.chelsea,
            minutes_played=90,
            goals=1,
            assists=0,
            is_starter=True,
            appearance_date=self.match_1.match_date.date(),
        )
        Appearance.objects.create(
            player=self.palmer,
            match=self.match_2,
            team=self.chelsea,
            minutes_played=90,
            goals=1,
            assists=0,
            is_starter=True,
            appearance_date=self.match_2.match_date.date(),
        )
        Appearance.objects.create(
            player=self.salah,
            match=self.match_2,
            team=self.liverpool,
            minutes_played=90,
            goals=1,
            assists=0,
            is_starter=True,
            appearance_date=self.match_2.match_date.date(),
        )
        Appearance.objects.create(
            player=self.saka,
            match=self.match_3,
            team=self.arsenal,
            minutes_played=85,
            goals=2,
            assists=0,
            is_starter=True,
            appearance_date=self.match_3.match_date.date(),
        )

    def test_team_list_returns_paginated_results(self):
        url = reverse("team-list")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

        names = [team["name"] for team in response.data["results"]]
        self.assertIn("Arsenal", names)
        self.assertIn("Chelsea", names)
        self.assertIn("Liverpool", names)

    def test_player_list_can_filter_by_team_and_name(self):
        url = reverse("player-list")

        response = self.client.get(
            url,
            {"team_id": self.arsenal.id, "name": "Saka"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Bukayo Saka")
        self.assertEqual(response.data["results"][0]["current_team"], self.arsenal.id)

    def test_match_list_can_filter_by_season_and_team(self):
        url = reverse("match-list")

        response = self.client.get(
            url,
            {"season": 2023, "team_id": self.chelsea.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        returned_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(returned_ids, {self.match_1.id, self.match_2.id})

    def test_match_detail_includes_nested_appearances(self):
        url = reverse("match-detail", kwargs={"pk": self.match_1.id})
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.match_1.id)
        self.assertEqual(response.data["home_team_name"], "Arsenal")
        self.assertEqual(response.data["away_team_name"], "Chelsea")
        self.assertEqual(len(response.data["appearances"]), 3)

        player_names = {item["player_name"] for item in response.data["appearances"]}
        self.assertEqual(player_names, {"Bukayo Saka", "Martin Odegaard", "Cole Palmer"})

    def test_team_players_endpoint_returns_only_that_teams_players(self):
        url = reverse("team-players", kwargs={"pk": self.arsenal.id})
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        names = {item["name"] for item in response.data["results"]}
        self.assertEqual(names, {"Bukayo Saka", "Martin Odegaard"})

    def test_player_appearances_endpoint_can_filter_by_season(self):
        url = reverse("player-appearances", kwargs={"pk": self.saka.id})
        response = self.client.get(url, {"season": 2023}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["team"], "Arsenal")
        self.assertEqual(response.data[0]["goals"], 1)
        self.assertEqual(response.data[0]["assists"], 1)
        self.assertEqual(response.data[0]["minutes_played"], 90)

    def test_top_scorers_endpoint_returns_expected_order_for_season(self):
        url = reverse("top-scorers")
        response = self.client.get(url, {"season": 2023, "limit": 3}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        self.assertEqual(response.data[0]["player_name"], "Cole Palmer")
        self.assertEqual(response.data[0]["total_goals"], 2)
        self.assertEqual(response.data[1]["player_name"], "Bukayo Saka")
        self.assertEqual(response.data[1]["total_goals"], 1)

    def test_top_assists_endpoint_returns_expected_player(self):
        url = reverse("top-assists")
        response = self.client.get(url, {"season": 2023, "limit": 3}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["player_name"], "Bukayo Saka")
        self.assertEqual(response.data[0]["total_assists"], 1)

    def test_most_minutes_endpoint_returns_expected_player(self):
        url = reverse("most-minutes")
        response = self.client.get(url, {"season": 2023, "limit": 3}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["player_name"], "Cole Palmer")
        self.assertEqual(response.data[0]["total_minutes"], 180)

    def test_team_top_scorers_endpoint_returns_expected_player(self):
        url = reverse("team-top-scorers", kwargs={"pk": self.arsenal.id})
        response = self.client.get(url, {"season": 2023, "limit": 5}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["team"], "Arsenal")
        self.assertEqual(response.data[0]["player_name"], "Bukayo Saka")
        self.assertEqual(response.data[0]["total_goals"], 1)

    def test_standings_endpoint_returns_correct_order_and_points(self):
        url = reverse("premier-league-standings")
        response = self.client.get(url, {"season": 2023}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        self.assertEqual(response.data[0]["team"], "Arsenal")
        self.assertEqual(response.data[0]["points"], 3)
        self.assertEqual(response.data[0]["position"], 1)

        self.assertEqual(response.data[1]["team"], "Liverpool")
        self.assertEqual(response.data[1]["points"], 1)
        self.assertEqual(response.data[1]["position"], 2)

        self.assertEqual(response.data[2]["team"], "Chelsea")
        self.assertEqual(response.data[2]["points"], 1)
        self.assertEqual(response.data[2]["position"], 3)