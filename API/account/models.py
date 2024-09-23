from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import validate_email,MinLengthValidator;
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken

class UserManager(BaseUserManager):
    def email_validator(self, email):
        domain = "@ritchennai.edu.in"
        if not email.endswith(domain):
            raise ValidationError(f"Invalid email domain. Must be {domain}")
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("Invalid email address")
        
    def create_user(self, email, full_name, reg_no, password=None,   **extra_fields):
        if not email:
            raise ValueError('User must provide an email address')
        if not reg_no :
            raise ValueError('User must provide a Register Number')
        
        email = self.normalize_email(email)
        self.email_validator(email)

        user = self.model(email=email, full_name= full_name, reg_no = reg_no,**extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)


        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if not email:
            raise ValueError('User must provide an email address')

        email = self.normalize_email(email)
        self.email_validator(email)

        user = self.model(email=email, full_name= full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=200, unique=True, verbose_name="E-Mail")
    full_name = models.CharField(max_length=100, verbose_name="Full Name")
    reg_no = models.CharField(max_length=25, blank=True, null=True, unique=True , validators= [MinLengthValidator(4)] ,verbose_name="Register Number")
    
    otp = models.CharField(max_length=4 , null= True , blank=True , verbose_name= "One Time Password" , )
    
    date_added = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_reset = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return self.full_name
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        } 

