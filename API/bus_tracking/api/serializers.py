from rest_framework import serializers
from bus_tracking.models import Route, Stop, RouteStatus, PassedStop

class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = '__all__'

class RouteSerializer(serializers.ModelSerializer):
    stops = StopSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = '__all__'

class PassedStopSerializer(serializers.ModelSerializer):
    stop = StopSerializer()

    class Meta:
        model = PassedStop
        fields = '__all__'

class RouteStatusSerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    passed_stops = PassedStopSerializer(many=True)
    upcoming_stop = StopSerializer()

    class Meta:
        model = RouteStatus
        fields = '__all__'
