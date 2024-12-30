from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

class APITests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_data(self):
        response = self.client.get(reverse('nba-data'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_teams(self):
        response = self.client.get(reverse('team-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_seasons(self):
        response = self.client.get(reverse('season-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_season_stats(self):
        response = self.client.get(reverse('season-stats', kwargs={'season_id': '2009-10'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)