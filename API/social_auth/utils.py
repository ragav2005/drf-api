from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from account.models import User

class Google:
    @staticmethod
    def validate(auth_token):
        try:
            id_info = id_token.verify_oauth2_token(auth_token , requests.Request())
            if "accounts.google.com" in id_info["iss"]:
                return id_info
            else:
                raise ValueError("Wrong issuer")
        except Exception as e:
            raise ValidationError('Invalid access token: {}'.format(e))
        
def login_google_user(email):
    
    user = User.objects.filter(email = email)
    
    if user.exists():
        user = user[0]
        if user.is_verified:
            user_tokens = user.tokens()
            return{
                'email': user.email,
                'full_name' : user.full_name,
                'reg_no' : user.reg_no,
                'access' : user_tokens.get('access'),
                'refresh' : user_tokens.get('refresh')
            } 
        else :
            raise ValidationError('User not verified')
    else :
         raise ValidationError('User not found or not registered')

    