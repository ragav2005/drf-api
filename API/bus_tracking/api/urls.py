from rest_framework.urls import path
from .views import RouteUpdateAPI

urlpatterns = [
    path('', RouteUpdateAPI.as_view(), name='route'),
    path('<str:route_number>', RouteUpdateAPI.as_view(), name='route'),
]
