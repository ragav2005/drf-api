from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .serializers import GoogleAuthSerializers

class GoogleAuthAPI(GenericAPIView):
    serializer_class = GoogleAuthSerializers
    
    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        print(serializer.validated_data)
        return Response(data , status=status.HTTP_200_OK)