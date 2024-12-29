from rest_framework import serializers
from .models import Season, Conference, Team, TeamStats

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'

class ConferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conference
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class TeamStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamStats
        fields = '__all__'