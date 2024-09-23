from random import randint
from email.message import EmailMessage
import smtplib
from account.models import User
from rest_framework import response,status


def get_otp():
    otp = ''
    for i in range(4):
        otp += str(randint(0,9))
    return otp;

def send_otp(email , reset = False ):
    otp = get_otp();
    
    if reset == False:
        subject = "OTP Verification"
        body = f"""\
            <html>
            <body>
                <p style="font-size: 16px; font-family: Arial, sans-serif;">
                    Your 6-digit code is:<br><br>
                    <strong style="font-size: 24px; color: #007BFF;">{otp}</strong><br><br>
                    This code can only be used once. It expires in 15 minutes.
                </p>
                <hr style="border: 1px solid #ddd;">
                <p style="font-size: 14px; font-family: Arial, sans-serif;">
                    © Robocraze<br>
                    TIF LABS PRIVATE LIMITED, Ground Floor, 912/10 Survey no. 104, 4th G street, Chelekare, Kalyan Nagar, 560043 Bengaluru KA, India<br><br>
                    <a href="http://example.com/privacy-policy" style="color: #007BFF;">Privacy policy</a>
                </p>
            </body>
            </html>
            """
    elif reset == True :
        subject = "Reset Password - OTP"
        body = f"""\
            <html>
            <body>
                <p style="font-size: 16px; font-family: Arial, sans-serif;">
                    Your 6-digit code is:<br><br>
                    <strong style="font-size: 24px; color: #007BFF;">{otp}</strong><br><br>
                    This code can only be used once. It expires in 15 minutes.
                </p>
                <hr style="border: 1px solid #ddd;">
                <p style="font-size: 14px; font-family: Arial, sans-serif;">
                    © Robocraze<br>
                    TIF LABS PRIVATE LIMITED, Ground Floor, 912/10 Survey no. 104, 4th G street, Chelekare, Kalyan Nagar, 560043 Bengaluru KA, India<br><br>
                    <a href="http://example.com/privacy-policy" style="color: #007BFF;">Privacy policy</a>
                </p>
            </body>
            </html>
            """
        
    server = smtplib.SMTP('smtp.gmail.com' , 587)
    server.starttls();
    server.login("ragavvignes2005@gmail.com", "rnnc evtc cybt eukg");

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = "ragavvignes2005@gmail.com"
    msg['TO'] = email;
    msg.set_content(body ,subtype='html')
    server.send_message(msg)
    
    user = User.objects.get(email = email)
    user.otp = otp;
    if  reset == True :
        user.is_reset = True
    user.save();

def handle_existing_user(email):
    existing_user = User.objects.filter(email = email).first()
    if existing_user:
        if existing_user.is_verified == False:
                existing_user.delete()
        else:
            return response.Response({"message" : "Email address already in use and verified."} , status=status.HTTP_400_BAD_REQUEST)

