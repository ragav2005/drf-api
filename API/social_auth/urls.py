from  django.urls import path
from .views import GoogleAuthAPI
urlpatterns = [
    path('google/', GoogleAuthAPI.as_view() , name="google-auth" )
]
