from django.db import models

class Season(models.Model):
    season_id = models.CharField(max_length=7, primary_key=True)
    start_year = models.IntegerField()
    end_year = models.IntegerField()

    class Meta:
        db_table = 'Seasons'

class Conference(models.Model):
    conference_id = models.CharField(max_length=1, primary_key=True)
    conference_name = models.CharField(max_length=10)

    class Meta:
        db_table = 'Conferences'

class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=100)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Teams'

class TeamStats(models.Model):
    stat_id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    average_offensive_rating = models.FloatField()
    average_defensive_rating = models.FloatField()
    average_net_rating = models.FloatField()
    average_plus_minus = models.FloatField()
    relative_net_rating = models.FloatField()
    relative_offensive_rating = models.FloatField()
    relative_defensive_rating = models.FloatField()

    class Meta:
        db_table = 'TeamStats'
        unique_together = ('team', 'season')