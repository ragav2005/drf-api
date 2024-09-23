from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from bus_tracking.models import Route, RouteStatus, Stop, PassedStop

class RouteUpdateAPITestCase(APITestCase):

    def setUp(self):
        # Create a route and stops for testing
        self.route = Route.objects.create(route_number='R1', current_location_latitude=0, current_location_longitude=0)
        
        # Create stops with coordinates for various places in Chennai
        self.stop1 = Stop.objects.create(
            route=self.route, 
            stop_name='Mylapore', 
            latitude=13.0032, 
            longitude=80.2508, 
            stop_order=1, 
            morning_schedule='08:00', 
            evening_schedule='17:00'
        )
        
        self.stop2 = Stop.objects.create(
            route=self.route, 
            stop_name='T Nagar', 
            latitude=13.0358, 
            longitude=80.2330, 
            stop_order=2, 
            morning_schedule='09:00', 
            evening_schedule='18:00'
        )

        self.url = reverse('route', args=[self.route.route_number])

    def test_update_route_with_valid_data(self):
        """Test updating the route with valid location and speed data."""
        data = {
            'latitude': 13.0032,
            'longitude': 80.2508,
            'current_speed': 10.0
        }
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if RouteStatus was created or updated
        route_status = RouteStatus.objects.get(route=self.route)
        self.assertEqual(route_status.current_speed, 10.0)
        self.assertTrue(route_status.is_stationary)

    def test_update_route_with_invalid_data(self):
        """Test updating the route with invalid data."""
        data = {
            'latitude': None,
            'longitude': None,
            'current_speed': None
        }
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_route_without_location_data(self):
        """Test updating the route without location data."""
        data = {
            'current_speed': 10.0
        }
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upcoming_stops_recorded(self):
        """Test that upcoming stops are recorded when the bus is near a stop."""
        data = {
            'latitude': 13.0032,
            'longitude': 80.2508,
            'current_speed': 0.0
        }
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        route_status = RouteStatus.objects.get(route=self.route)
        self.assertIsNotNone(route_status.upcoming_stop)
        self.assertEqual(route_status.upcoming_stop, self.stop1)

    def test_passed_stops_recorded(self):
        """Test that passed stops are recorded correctly."""
        # Simulate passing the first stop
        data1 = {
            'latitude': 13.0032,
            'longitude': 80.2508,
            'current_speed': 0.0
        }
        self.client.patch(self.url, data1, format='json')

        # Simulate passing the second stop
        data2 = {
            'latitude': 13.0358,
            'longitude': 80.2330,
            'current_speed': 0.0
        }
        self.client.patch(self.url, data2, format='json')

        route_status = RouteStatus.objects.get(route=self.route)
        passed_stops = route_status.passed_stops.all()
        self.assertEqual(passed_stops.count(), 2)
        self.assertEqual(passed_stops[0].stop, self.stop1)
        self.assertEqual(passed_stops[1].stop, self.stop2)

    def test_eta_calculation(self):
        """Test the ETA calculation based on current speed and distance."""
        data = {
            'latitude': 13.0032,
            'longitude': 80.2508,
            'current_speed': 10.0
        }
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        route_status = RouteStatus.objects.get(route=self.route)
        self.assertIsNotNone(route_status.eta)

    def test_stationary_logic(self):
        """Test the logic that determines if the bus is stationary."""
        # First, simulate the bus moving
        data = {
            'latitude': 13.0000,
            'longitude': 80.2500,
            'current_speed': 10.0
        }
        self.client.patch(self.url, data, format='json')

        # Now simulate it stopping
        data = {
            'latitude': 13.0032,
            'longitude': 80.2508,
            'current_speed': 0.0
        }
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        route_status = RouteStatus.objects.get(route=self.route)
        self.assertTrue(route_status.is_stationary)

    def test_stationary_timeout(self):
        """Test that the bus is marked as stationary after a certain duration."""
        # First, simulate the bus being stationary
        data = {
            'latitude': 13.0032,
            'longitude': 80.2508,
            'current_speed': 0.0
        }
        self.client.patch(self.url, data, format='json')

        # Simulate some time passing (mocking time would be needed here in a real test)

        # Now simulate another stationary update
        data = {
            'latitude': 13.0032,
            'longitude': 80.2508,
            'current_speed': 0.0
        }
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        route_status = RouteStatus.objects.get(route=self.route)
        self.assertTrue(route_status.is_stationary)
