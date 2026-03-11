import csv
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from football.models import Team, Player, Match, Appearance


class Command(BaseCommand):
    help = "Import football data from CSV files into the database"

    EPL_COMPETITION_ID = "GB1"

    def handle(self, *args, **kwargs):
        base_dir = Path(__file__).resolve().parents[4]
        data_dir = base_dir / "COMP3011-Coursework1" / "data"

        clubs_file = data_dir / "clubs.csv"
        players_file = data_dir / "players.csv"
        games_file = data_dir / "games.csv"
        appearances_file = data_dir / "appearances.csv"

        if not clubs_file.exists():
            self.stdout.write(self.style.ERROR(f"Missing file: {clubs_file}"))
            return
        if not players_file.exists():
            self.stdout.write(self.style.ERROR(f"Missing file: {players_file}"))
            return
        if not games_file.exists():
            self.stdout.write(self.style.ERROR(f"Missing file: {games_file}"))
            return
        if not appearances_file.exists():
            self.stdout.write(self.style.ERROR(f"Missing file: {appearances_file}"))
            return

        with transaction.atomic():
            self.import_clubs(clubs_file)
            self.import_players(players_file)
            self.import_games(games_file)
            self.import_appearances(appearances_file)

        self.stdout.write(self.style.SUCCESS("EPL import completed successfully."))

    # ----------------------------------
    # CLUBS
    # ----------------------------------

    def import_clubs(self, filepath):

        self.stdout.write("Importing EPL clubs...")

        count = 0

        with open(filepath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:

                if row["domestic_competition_id"] != self.EPL_COMPETITION_ID:
                    continue

                Team.objects.update_or_create(
                    external_id=row["club_id"],
                    defaults={
                        "name": row["name"],
                        "short_name": row["club_code"],
                        "country": "England",
                        "competition": "Premier League",
                        "stadium": row["stadium_name"],
                        "founded": None,
                        "logo_url": row["url"],
                    },
                )

                count += 1

        self.stdout.write(self.style.SUCCESS(f"EPL clubs imported: {count}"))

    # ----------------------------------
    # PLAYERS
    # ----------------------------------

    def import_players(self, filepath):

        self.stdout.write("Importing EPL players...")

        teams = {t.external_id: t for t in Team.objects.all()}

        count = 0

        with open(filepath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:

                club_id = row["current_club_id"]

                if club_id not in teams:
                    continue

                Player.objects.update_or_create(
                    external_id=row["player_id"],
                    defaults={
                        "name": row["name"],
                        "full_name": f"{row['first_name']} {row['last_name']}",
                        "date_of_birth": self.safe_date(row["date_of_birth"]),
                        "nationality": row["country_of_citizenship"],
                        "position": row["position"],
                        "current_team": teams.get(club_id),
                        "market_value": self.safe_int(row["market_value_in_eur"]),
                        "height_cm": self.safe_int(row["height_in_cm"]),
                        "preferred_foot": row["foot"],
                        "image_url": row["image_url"],
                    },
                )

                count += 1

                if count % 1000 == 0:
                    self.stdout.write(f"{count} players processed...")

        self.stdout.write(self.style.SUCCESS(f"EPL players imported: {count}"))

    # ----------------------------------
    # GAMES
    # ----------------------------------

    def import_games(self, filepath):

        self.stdout.write("Importing EPL games...")

        teams = {t.external_id: t for t in Team.objects.all()}

        count = 0

        with open(filepath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:

                if row["competition_id"] != self.EPL_COMPETITION_ID:
                    continue

                home_team = teams.get(row["home_club_id"])
                away_team = teams.get(row["away_club_id"])

                if not home_team or not away_team:
                    continue

                Match.objects.update_or_create(
                    external_id=row["game_id"],
                    defaults={
                        "competition": "Premier League",
                        "season": self.safe_int(row["season"]),
                        "match_date": self.safe_datetime(row["date"]),
                        "home_team": home_team,
                        "away_team": away_team,
                        "home_score": self.safe_int(row["home_club_goals"]),
                        "away_score": self.safe_int(row["away_club_goals"]),
                        "venue": row["stadium"],
                        "attendance": self.safe_int(row["attendance"]),
                    },
                )

                count += 1

                if count % 500 == 0:
                    self.stdout.write(f"{count} matches processed...")

        self.stdout.write(self.style.SUCCESS(f"EPL matches imported: {count}"))

    # ----------------------------------
    # APPEARANCES
    # ----------------------------------

    def import_appearances(self, filepath):

        self.stdout.write("Importing EPL appearances...")

        players = {p.external_id: p for p in Player.objects.all()}
        matches = {m.external_id: m for m in Match.objects.all()}
        teams = {t.external_id: t for t in Team.objects.all()}

        count = 0
        skipped = 0

        with open(filepath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:

                player = players.get(row["player_id"])
                match = matches.get(row["game_id"])
                team = teams.get(row["player_club_id"])

                if not player or not match or not team:
                    skipped += 1
                    continue

                Appearance.objects.update_or_create(
                    player=player,
                    match=match,
                    team=team,
                    defaults={
                        "minutes_played": self.safe_int(row["minutes_played"]),
                        "goals": self.safe_int(row["goals"]) or 0,
                        "assists": self.safe_int(row["assists"]) or 0,
                        "yellow_cards": self.safe_int(row["yellow_cards"]) or 0,
                        "red_cards": self.safe_int(row["red_cards"]) or 0,
                        "appearance_date": self.safe_date(row["date"]),
                    },
                )

                count += 1

                if count % 10000 == 0:
                    self.stdout.write(f"{count} appearances processed...")

        self.stdout.write(self.style.SUCCESS(f"EPL appearances imported: {count}"))
        self.stdout.write(self.style.WARNING(f"Skipped rows: {skipped}"))

    # ----------------------------------
    # HELPERS
    # ----------------------------------

    def safe_int(self, value):

        try:
            if value in ["", None]:
                return None
            return int(float(value))
        except:
            return None

    def safe_date(self, value):

        if not value:
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except:
            return None

    def safe_datetime(self, value):

        if not value:
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except:
            return None