from django.db import models

class Route(models.Model):
    route_number = models.CharField(max_length=100)
    current_location_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_location_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    driver_name = models.CharField(max_length=50, null=True)
    driver_contact = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.route_number


class Stop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    stop_name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    stop_order = models.PositiveIntegerField()
    morning_schedule = models.TimeField()
    evening_schedule = models.TimeField()
    
    class Meta:
        ordering = ['stop_order']

    def __str__(self):
        return f'{self.stop_name} (Order: {self.stop_order})'



class RouteStatus(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    is_stationary = models.BooleanField(default=False)
    current_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    last_update_time = models.DateTimeField(auto_now=True)
    stationary_start_time = models.DateTimeField(null=True, blank=True)
    average_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    eta = models.IntegerField(null=True, blank=True)
    upcoming_stop = models.ForeignKey(Stop, related_name='upcoming_stop', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.route.route_number} status'

class PassedStop(models.Model):
    route_status = models.ForeignKey('RouteStatus', on_delete=models.CASCADE, related_name='passed_stops')
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

    class Meta:
        unique_together = ('route_status', 'stop')


class RouteLocation(models.Model):
    route_status = models.ForeignKey(RouteStatus, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('route_status', 'timestamp')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if RouteLocation.objects.filter(route_status=self.route_status).count() > 3:
            oldest_location = RouteLocation.objects.filter(route_status=self.route_status).order_by('timestamp').first()
            if oldest_location:
                oldest_location.delete()


class RouteSpeed(models.Model):
    route_status = models.ForeignKey(RouteStatus, on_delete=models.CASCADE)
    speed = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if RouteSpeed.objects.filter(route_status=self.route_status).count() > 5:
            oldest_speed = RouteSpeed.objects.filter(route_status=self.route_status).order_by('timestamp').first()
            if oldest_speed:
                oldest_speed.delete()