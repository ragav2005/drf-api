from django.db import IntegrityError
from psycopg2 import errorcodes

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status,permissions

from .serializers import *
from account.models import User
from .utils import send_otp,  handle_existing_user

# Create your views here.

class RegisterAPI(GenericAPIView):
    serializer_class = RegisterSerializer
    
    def post(self,request):
        
        try :
            email = dict(request.data)['email']
            # reg_no = dict(request.data)['reg_no']
            handle_existing_user(email)
            # handle_duplicate_reg_no(reg_no)   
        except Exception as e :
            return Response({"error" : str(e)}) 
        
        serializer = self.serializer_class(data=request.data)
        otp_status = "sent"
        if  serializer.is_valid():
            
            #existing user Check
            email = serializer.validated_data['email']
            
                    
            #user registration
            try :
                serializer.save()
                user = serializer.data
                try :
                    send_otp(user['email'])
                except Exception as e :
                    otp_status = {
                        'status' : "Failed" ,
                        'message' : e
                    }
                    
                return Response({
                    "data" : user,
                    "OTP" : otp_status
                } , status=status.HTTP_201_CREATED)
                
            except IntegrityError as e:
                return Response({
                    'message': 'An error occurred while creating the user. Please try again.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPAPI(GenericAPIView):
    
    def post(self, request):
        serializer = VerifyOTPSerializer(data = request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            otp = serializer.data['otp']
            user = User.objects.filter(email = email)
            if user.exists():
                user = user.first()
                if user.is_verified == False:
                    if user.otp == otp :
                        user.is_verified = True
                        user.otp = None
                        user.save()
                        return Response({
                                        "email": email,
                                        "message" : "OTP Verified Successfully",
                                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                                        "email": email,
                                        "error" : "Invalid OTP ",
                                        }, status=status.HTTP_400_BAD_REQUEST)
                else : 
                    return Response({
                                    "email": email,
                                    "error" : "User Already Verified ",

                                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                                    "email": email,
                                    "error" : "Can Not find your email",
                                    }, status=status.HTTP_400_BAD_REQUEST)
        else: 
            return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

class LoginAPI(GenericAPIView):
    serializer_class = LoginSerializers
    
    def post(self, request):
        serializer = self.serializer_class(data = request.data , context = {"request" : request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data , status=status.HTTP_200_OK)
    
class ResetPasswordOTP_API(GenericAPIView):
    
    def post(self, request):
        serializer = ResetPasswordOTPSerializers(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            try:
                if user: 
                    send_otp(user.email, reset=True)
                    otp_status = {
                        'email': str(email),
                        'status': "sent",} 
                    
                else:
                    otp_status = {
                        'email': str(email),
                        'status': "Failed",
                        'message': "User not found"
                    }
            except Exception as e:
                otp_status = {
                    'email': str(email),
                    'status': "Failed",
                    'message': str(e)
                }
            return Response(otp_status, status=status.HTTP_200_OK)  # Use 200 OK for successful processing
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
           
class ResetPasswordAPI(GenericAPIView):
    serializer_class = ResetPasswordSerializers
    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']
            user = User.objects.filter(email = serializer.validated_data['email']).first()
            if user.otp != None :
                user.set_password(password)
                user.is_reset = False;
                user.otp = None;
                user.save();
                return Response({
                    "email" : serializer.data['email'],
                    "message" : "Password Reset Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Internal Server Error. Try again "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
            
class LogoutAPI(GenericAPIView):
    serializer_class = LogOutSerializers
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message" : "logout sucess"} , status=status.HTTP_204_NO_CONTENT) 