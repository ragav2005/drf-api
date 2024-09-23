from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from account.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length = 100 , min_length = 8 ,write_only = True)
    password2 = serializers.CharField(max_length = 100 , min_length = 8 ,write_only = True)
    
    class Meta:
        model = User
        fields = ['email' , 'full_name' , 'reg_no', 'password' , 'password2' ]
    
    def validate(self,attrs):
        email = attrs.get('email' , '')
        password = attrs.get('password' , '')
        password2 = attrs.get('password2' , '')
        reg_no = attrs.get('reg_no')
        domain = "@ritchennai.edu.in"
        
        if not email.endswith(domain):
            raise ValidationError(f"Invalid email domain. Must be {domain}")
        
        if password != password2 :
            raise ValidationError("Passwords doesn't match")
        
        return attrs
    
    def is_valid(self, raise_exception=True):
        # Perform base validation
        valid = super().is_valid(raise_exception=False)
        
        data = self.initial_data
        reg_no = data.get('reg_no')
        if reg_no:
            user = User.objects.filter(reg_no=reg_no).first()
            if user:
                self._errors['reg_no'] = [f'Register number : {reg_no} already used by {user.email}']
                valid = False
                   
        
        if not valid and raise_exception:
            raise serializers.ValidationError(self._errors)
        return valid
    # def is_valid(self, raise_exception=True):
    #     valid = super().is_valid(raise_exception=False)

    #     data = self.initial_data
    #     reg_no = data.get('reg_no')

    #     if reg_no:
    #         existing_user = User.objects.filter(reg_no=reg_no).first()
    #         if existing_user:
    #             error_message = f"Register number {reg_no} is already used by {existing_user.email}"
    #             if raise_exception:
    #                 raise serializers.ValidationError({"reg_no": error_message ,})
                    
    #             return False

    #     return valid

 
    def create(self , validated_data):    
        return User.objects.create_user(
            email = validated_data['email'],
            full_name = validated_data['full_name'],
            reg_no = validated_data['reg_no'],
            password = validated_data['password'],
        )
        
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length = 200)
    otp = serializers.CharField(max_length = 4 , min_length = 4)
    
class LoginSerializers(serializers.ModelSerializer):
    
    email = serializers.EmailField(max_length = 200 )
    password = serializers.CharField(max_length = 100 , min_length = 8 , write_only = True)
    full_name = serializers.CharField(max_length = 100 , read_only = True) 
    access = serializers.CharField(max_length = 255 , read_only = True)
    refresh = serializers.CharField(max_length = 255 , read_only = True)
    reg_no = serializers.CharField(max_length = 25, read_only=True)
    
    class Meta:
        model = User
        fields = ['email' , 'reg_no' ,'password' , 'full_name' , 'access' , 'refresh']
    
    def validate(self , attrs):
        
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(request , email = email , password= password)
        
        if not User.objects.filter(email = email).exists():
            raise AuthenticationFailed("Failed. Email not found or Invalid")        
        if not user :
            raise AuthenticationFailed("Failed. Invalid crentials ")
        if not user.is_verified :
            raise AuthenticationFailed("Failed. Your account is not verified ")
        
        tokens = user.tokens()
        
        return {
            'email' : user.email,
            'full_name': user.full_name,
            'reg_no' : user.reg_no,
            'access' : str(tokens.get('access')),
            'refresh' : str(tokens.get('refresh')),
        }
        
class ResetPasswordSerializers(serializers.Serializer):
    password = serializers.CharField(max_length = 100 , min_length = 8 ,write_only = True)
    password2 = serializers.CharField(max_length = 100 , min_length = 8 ,write_only = True)
    email = serializers.EmailField(max_length=200)
    otp = serializers.CharField(max_length = 4 , min_length = 4 , write_only = True)
    
    class Meta:
        fields = ['password' , 'password2' , 'email' , 'otp']
    
    def validate(self , attrs) :
        email = attrs.get('email')
        password = attrs.get('password')
        password2 = attrs.get('password2')
        otp = attrs.get('otp')
        
        user = User.objects.filter(email = email).first()
        
        if not user:
            raise ValidationError("Failed. Email not found ")
        if  not user.is_verified:
            raise ValidationError("Failed. Your account is not verified ")
        if not user.is_reset:
            raise ValidationError("Failed. Invalid state ")
        if password != password2:
            raise ValidationError("Failed. Passwords do not match ")
        
        return attrs

class ResetPasswordOTPSerializers(serializers.Serializer):
    email = serializers.EmailField(max_length = 200)
    
    class Meta:
        fields = ['email']
    
    def validate(self, attrs):
        email = attrs.get('email')
        
        user = User.objects.filter(email = email).first()
        
        if not user:
            raise ValidationError("Failed. Email not found ")
        if  not user.is_verified:
            raise ValidationError("Failed. Your account is not verified ")
        if  user.is_reset:
            raise ValidationError("Failed. You already requested OTP to reset ")

        return attrs
        
class LogOutSerializers(serializers.Serializer):
    
    refresh = serializers.CharField()  
    
    default_error_messages = {
        'bad_token' : 'token is expired or invalid'
    }
    def validate(self, attrs):
        self.refresh = attrs.get("refresh")
        return attrs
    
    def save(self, **kwargs):
        try:
            refresh = RefreshToken(self.refresh).blacklist()
        except TokenError :
            self.fail("bad_token")


        
        

       
        
