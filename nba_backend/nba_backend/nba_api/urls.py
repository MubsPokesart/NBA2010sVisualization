from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.NBADataView.as_view(), name='nba-data'),
    path('update/', views.UpdateDataView.as_view(), name='update-data'),
    path('teams/', views.TeamListView.as_view(), name='team-list'),
    path('seasons/', views.SeasonListView.as_view(), name='season-list'),
    path('stats/<str:season_id>/', views.SeasonStatsView.as_view(), name='season-stats'),
    # Add a root API endpoint that returns available endpoints
    path('', views.APIRootView.as_view(), name='api-root'),
]