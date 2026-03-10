from django.db import models

# Create your models here.

class Team(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=20)
    stadium_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name