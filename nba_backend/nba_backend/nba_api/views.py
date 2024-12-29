from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils.data_handler import fetch_decade_data, force_kaggle_update
from .serializers import TeamStatsSerializer
from .models import TeamStats, Season, Team

class NBADataView(APIView):
    def get(self, request):
        try:
            data = fetch_decade_data()
            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateDataView(APIView):
    def post(self, request):
        try:
            force_kaggle_update()
            return Response({'message': 'Data updated successfully'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TeamListView(APIView):
    def get(self, request):
        teams = Team.objects.all().values('team_id', 'team_name', 'conference__conference_name')
        return Response(teams)

class SeasonListView(APIView):
    def get(self, request):
        seasons = Season.objects.all().values()
        return Response(seasons)

class SeasonStatsView(APIView):
    def get(self, request, season_id):
        stats = TeamStats.objects.filter(season_id=season_id)
        serializer = TeamStatsSerializer(stats, many=True)
        return Response(serializer.data)

class APIRootView(APIView):
    def get(self, request):
        return Response({
            'data': request.build_absolute_uri('data/'),
            'update': request.build_absolute_uri('update/'),
            'teams': request.build_absolute_uri('teams/'),
            'seasons': request.build_absolute_uri('seasons/'),
            'stats': request.build_absolute_uri('stats/'),
        })
