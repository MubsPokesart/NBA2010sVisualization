from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from .utils.data_handler import AsyncUpdateManager

class NBAAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Reset AsyncUpdateManager state before each test
        AsyncUpdateManager._updating = False
        
        # Sample test data
        self.sample_data = {
            "2009-10": [
                {
                    "team": "Test Team",
                    "conference": "Western",
                    "average_offensive_rating": 100.0,
                    "average_defensive_rating": 95.0,
                    "average_net_rating": 5.0,
                    "average_plus_minus": 3.0,
                    "relative_net_rating": 2.0,
                    "relative_offensive_rating": 1.0,
                    "relative_defensive_rating": -1.0
                }
            ]
        }

    @patch('nba_api.views.fetch_decade_data')
    def test_nba_data_view_success(self, mock_fetch):
        """Test successful data retrieval"""
        mock_fetch.return_value = (self.sample_data, False)
        response = self.client.get(reverse('nba-data'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.sample_data)

    @patch('nba_api.views.fetch_decade_data')
    def test_nba_data_view_needs_update(self, mock_fetch):
        """Test response when data needs update"""
        mock_fetch.return_value = (None, True)
        response = self.client.get(reverse('nba-data'))
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch('nba_api.views.fetch_teams_in_year_data')
    def test_team_list_view_success(self, mock_fetch):
        """Test successful team list retrieval"""
        sample_teams = ["Team 1", "Team 2"]
        mock_fetch.return_value = sample_teams
        response = self.client.get(reverse('team-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, sample_teams)

    @patch('nba_api.views.fetch_decade_data')
    @patch('nba_api.views.get_seasons_in_decade_data')
    def test_season_list_view_success(self, mock_get_seasons, mock_fetch_data):
        """Test successful season list retrieval"""
        mock_fetch_data.return_value = (self.sample_data, False)
        sample_seasons = ["2009-10", "2010-11"]
        mock_get_seasons.return_value = sample_seasons
        
        response = self.client.get(reverse('season-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, sample_seasons)

    @patch('nba_api.views.fetch_decade_data')
    @patch('nba_api.views.fetch_season_in_decade_data')
    def test_season_stats_view_success(self, mock_fetch_season, mock_fetch_data):
        """Test successful season stats retrieval"""
        mock_fetch_data.return_value = (self.sample_data, False)
        season_stats = self.sample_data["2009-10"]
        mock_fetch_season.return_value = season_stats
        
        response = self.client.get(reverse('season-stats', kwargs={'season_id': '2009-10'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, season_stats)

    def test_update_status_view(self):
        """Test update status retrieval"""
        response = self.client.get(reverse('update-status'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"updating": False})

    def test_update_view(self):
        """Test update endpoint"""
        response = self.client.post(reverse('update-data'))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_view_already_updating(self):
        """Test update endpoint when update is already in progress"""
        AsyncUpdateManager._updating = True
        response = self.client.post(reverse('update-data'))
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_api_unavailable_during_update(self):
        """Test all endpoints return 503 during update"""
        AsyncUpdateManager._updating = True
        
        # Test all endpoints except update
        endpoints = [
            reverse('nba-data'),
            reverse('team-list'),
            reverse('season-list'),
            reverse('season-stats', kwargs={'season_id': '2009-10'})
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code, 
                status.HTTP_503_SERVICE_UNAVAILABLE,
                f"Endpoint {endpoint} should return 503 during update"
            )

    @patch('nba_api.views.fetch_decade_data')
    def test_error_handling(self, mock_fetch):
        """Test error handling in views"""
        mock_fetch.side_effect = Exception("Test error")
        response = self.client.get(reverse('nba-data'))
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)