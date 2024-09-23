from datetime import timedelta
from django.utils import timezone
from geopy.distance import geodesic
from .models import RouteLocation, RouteSpeed
from bus_tracking.models import PassedStop
import requests  # Change from httpx to requests

# Constants
SPEED_THRESHOLD = 5  # Speed threshold in km/h to detect stationary
STOP_TIME_THRESHOLD_MINUTES = 5  # Time to confirm the bus is stationary (minutes)
GEOFENCE_RADIUS = 0.07  # 70 meters radius for the geofence around the stop

def calculate_eta(distance, average_speed):
    if distance is None or average_speed is None or average_speed == 0:
        return None
    return (distance / float(average_speed)) * 60

def get_distance(start, end):
    try:
        url = "http://localhost:8080/route"
        params = {
            "point": [f"{start[0]},{start[1]}", f"{end[0]},{end[1]}"],
            "profile": "car",
            "locale": "en",
            "instructions": "false",
            "calc_points": "false",
            "type": "json"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            distance_meters = data['paths'][0]['distance']
            return distance_meters / 1000  # Convert to kilometers
        else:
            return response.status_code  # Return status code on error
    except Exception as e:
        return str(e)

def check_stationary(current_speed, route_status):
    recent_locations = list(RouteLocation.objects.filter(route_status=route_status).order_by('-timestamp')[:3])
    location_queue = [(loc.latitude, loc.longitude) for loc in recent_locations]

    if len(location_queue) > 1:
        distances = [
            geodesic(location_queue[i], location_queue[i + 1]).meters
            for i in range(len(location_queue) - 1)
        ]
        within_geofence = all(distance < GEOFENCE_RADIUS for distance in distances)

        if float(current_speed) < SPEED_THRESHOLD and within_geofence:
            if route_status.stationary_start_time is None:
                route_status.stationary_start_time = timezone.now()
                route_status.save()
                return False
            else:
                time_stationary = timezone.now() - route_status.stationary_start_time
                return time_stationary > timedelta(minutes=STOP_TIME_THRESHOLD_MINUTES)
        else:
            if route_status.stationary_start_time is not None:
                route_status.stationary_start_time = None
                route_status.save()
            return False 

    return False

def average_speed(current_speed, route_status):
    speeds = list(RouteSpeed.objects.filter(route_status=route_status).order_by('-timestamp')[:5])
    if speeds and len(speeds) > 1:
        total_speed = sum(speed.speed for speed in speeds)
        return total_speed / len(speeds)
    return current_speed if current_speed else None

def update_stops(route_status, current_location):
    passed_stops = list(route_status.passed_stops.all())
    current_time = timezone.now()
    upcoming_stops = []

    all_stops = list(route_status.route.stops.all())

    for stop in all_stops:
        stop_location = (stop.latitude, stop.longitude)

        if is_near_stop(current_location, stop_location):
            if not any(passed_stop.stop == stop for passed_stop in passed_stops):
                PassedStop.objects.create(route_status=route_status, stop=stop, timestamp=current_time)
        else:
            if not any(passed_stop.stop == stop for passed_stop in passed_stops):
                upcoming_stops.append(stop)

    next_stop = upcoming_stops[0] if upcoming_stops else None
    return passed_stops, next_stop, upcoming_stops

def is_near_stop(current_location, stop_location):
    distance_to_stop = geodesic(current_location, stop_location).meters
    return distance_to_stop <= GEOFENCE_RADIUS
