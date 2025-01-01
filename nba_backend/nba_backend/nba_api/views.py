from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils.data_handler import (
    fetch_decade_data, 
    force_kaggle_update, 
    fetch_teams_in_year_data,
    get_seasons_in_decade_data,
    fetch_season_in_decade_data
)
from .serializers import TeamStatsSerializer
from .models import TeamStats, Season, Team
from django.db import DatabaseError
import asyncio
import threading

class AsyncUpdateManager:
    _updating = False
    
    @classmethod
    def is_updating(cls):
        return cls._updating
    
    @classmethod
    def set_updating(cls, state):
        cls._updating = state

class BaseAPIView(APIView):
    def dispatch(self, request, *args, **kwargs):
        if AsyncUpdateManager.is_updating() and not isinstance(self, UpdateDataView):
            return Response(
                {"error": "Database is currently updating. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        return super().dispatch(request, *args, **kwargs)

class NBADataView(BaseAPIView):
    def get(self, request):
        try:
            data, needs_update = fetch_decade_data()
            if needs_update:
                # Start background update
                def update_process():
                    AsyncUpdateManager.set_updating(True)
                    try:
                        force_kaggle_update()
                    finally:
                        AsyncUpdateManager.set_updating(False)

                threading.Thread(target=update_process).start()
                
                return Response(
                    {"error": "Data update in progress. Please try again later."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            if data is None:
                return Response(
                    {"error": "No data available"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateDataView(BaseAPIView):
    def post(self, request):
        if AsyncUpdateManager.is_updating():
            return Response(
                {"error": "Update already in progress"},
                status=status.HTTP_409_CONFLICT
            )

        def update_process():
            AsyncUpdateManager.set_updating(True)
            try:
                force_kaggle_update()
            finally:
                AsyncUpdateManager.set_updating(False)

        # Start update in background
        threading.Thread(target=update_process).start()

        return Response(
            {'message': 'Update process started'},
            status=status.HTTP_202_ACCEPTED
        )

class TeamListView(BaseAPIView):
    # The information returned by this view is not dependent on the status of the underlying database
    # So no logic to check if the database is functioning is required
    def get(self, request):
        try:
            teams = fetch_teams_in_year_data()
            if teams is None:
                return Response(
                    {"error": "No team data available"},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(teams)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SeasonListView(BaseAPIView):
    def get(self, request):

        try:
            data, needs_update = fetch_decade_data()
            if needs_update:
                return Response(
                    {"error": "Data update in progress. Please try again later."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            seasons = get_seasons_in_decade_data(data)

            if not seasons:
                return Response(
                    {"error": "No season data available"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(seasons)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SeasonStatsView(BaseAPIView):
    def get(self, request, season_id):
        try:
            data, needs_update = fetch_decade_data()
            if needs_update:
                return Response(
                    {"error": "Data update in progress. Please try again later."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            stats = fetch_season_in_decade_data(data, season_id)
            if stats is None:
                return Response(
                    {"error": f"No data available for season {season_id}"},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(stats)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class UpdateStatusView(BaseAPIView):
    def get(self, request):
        return Response({
            "updating": AsyncUpdateManager.is_updating()
        })