from django.db import models


class Team(models.Model):
    external_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=100, blank=True)
    competition = models.CharField(max_length=100, blank=True)
    season = models.IntegerField(null=True, blank=True)
    stadium = models.CharField(max_length=100, blank=True)
    founded = models.IntegerField(null=True, blank=True)
    logo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    external_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=150, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=50, blank=True)
    current_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="players"
    )
    market_value = models.BigIntegerField(null=True, blank=True)
    height_cm = models.IntegerField(null=True, blank=True)
    preferred_foot = models.CharField(max_length=20, blank=True)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Match(models.Model):
    external_id = models.CharField(max_length=50, unique=True)
    competition = models.CharField(max_length=100, blank=True)
    season = models.IntegerField(null=True, blank=True)
    match_date = models.DateTimeField()
    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="home_matches"
    )
    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="away_matches"
    )
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    venue = models.CharField(max_length=100, blank=True)
    attendance = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"


class Appearance(models.Model):
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="appearances"
    )
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="appearances"
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="appearances"
    )
    minutes_played = models.IntegerField(null=True, blank=True)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)
    position_played = models.CharField(max_length=50, blank=True)
    rating = models.FloatField(null=True, blank=True)
    is_starter = models.BooleanField(default=False)
    appearance_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("player", "match", "team")

    def __str__(self):
        return f"{self.player} - {self.match}"