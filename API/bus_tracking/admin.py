from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Route)
admin.site.register(Stop)
admin.site.register(PassedStop)
admin.site.register(RouteStatus)
admin.site.register(RouteLocation)
admin.site.register(RouteSpeed)