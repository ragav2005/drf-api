from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status
from bus_tracking.models import Route, RouteStatus, RouteLocation, RouteSpeed
from .serializers import RouteStatusSerializer, PassedStopSerializer, StopSerializer
from bus_tracking.utils import (
    calculate_eta, 
    average_speed, 
    check_stationary, 
    update_stops, 
    get_distance
)

class RouteUpdateAPI(APIView):

    def patch(self, request, route_number):
        data = request.data
        route = get_object_or_404(Route, route_number=route_number)
        route_status, created = RouteStatus.objects.get_or_create(route=route)

        # Update current location
        route.current_location_latitude = data.get('latitude')
        route.current_location_longitude = data.get('longitude')
        current_speed = data.get('current_speed')
        current_location = (data.get('latitude'), data.get('longitude'))

        # Create RouteLocation and RouteSpeed
        RouteLocation.objects.create(
            route_status=route_status, 
            latitude=data.get('latitude'), 
            longitude=data.get('longitude')
        )
        RouteSpeed.objects.create(
            route_status=route_status, 
            speed=current_speed
        )

        # Update the route status
        route_status.current_speed = current_speed
        route_status.average_speed = average_speed(current_speed, route_status)
        route_status.is_stationary = check_stationary(current_speed, route_status)

        # Update stops and ETA
        passed_stops, next_stop, upcoming_stops = update_stops(route_status, current_location)
        route_status.upcoming_stop = next_stop

        if next_stop:
            distance_to_next_stop = get_distance(
                current_location, 
                (next_stop.latitude, next_stop.longitude)
            )
            route_status.eta = calculate_eta(distance_to_next_stop, route_status.average_speed)

        # Save route and route status
        route_status.save()
        route.save()

        # Serialize the response data
        serializer = RouteStatusSerializer(route_status)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, route_number):
        route_status = get_object_or_404(RouteStatus, route__route_number=route_number)
        route = route_status.route
        current_location = (route.current_location_latitude, route.current_location_longitude)

        # Update the stop status
        passed_stops, next_stop, upcoming_stops = update_stops(route_status, current_location)

        # Serialize the passed and upcoming stops
        passed_stops_serialized = PassedStopSerializer(passed_stops, many=True).data
        upcoming_stops_serialized = StopSerializer(upcoming_stops, many=True).data

        # Serialize route status and combine the data with passed and upcoming stops
        serializer = RouteStatusSerializer(route_status)
        response_data = {
            **serializer.data,
            'passed_stops': passed_stops_serialized,
            'upcoming_stops': upcoming_stops_serialized,
        }

        return Response(response_data)
