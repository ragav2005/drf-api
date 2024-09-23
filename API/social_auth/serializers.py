from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import AuthenticationFailed
from .utils import Google , login_google_user

client_id = "640924192317-vfbesmhl7h4fuopl3tq8lr6b0hvjc6ks.apps.googleusercontent.com"

class GoogleAuthSerializers(serializers.Serializer):
    
    auth_token = serializers.CharField()
    
    def validate_auth_token(self,auth_token):
        domain = "@ritchennai.edu.in"
        user_data = Google.validate(auth_token)
        print(user_data)
        
        try :
            user_data['sub']
        except ValidationError:
            raise serializers.ValidationError('invalid google auth token')
        
        if user_data['aud'] != client_id:
            raise AuthenticationFailed("invalid cilent id for google auth")
        
        email = user_data['email']
        
        if not email.endswith(domain):
            raise ValidationError(f"invalid email domain. must be {domain}")
        
        return login_google_user(email)
        
        
        
        
        
        
        