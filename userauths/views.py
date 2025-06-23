from django.shortcuts import render
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Profile
from .serializer import MyTokenObtainPairSerializer, RegisterSerializer, UserSerializer, ProfileSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
import random
import shortuuid
from rest_framework.response import Response
from rest_framework import status



# This code defines a DRF View class called MyTokenObtainPairView, which inherits from TokenObtainPairView.
class MyTokenObtainPairView(TokenObtainPairView):
    # Here, it specifies the serializer class to be used with this view.
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    #get all users as a queryset
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


#creating unique key for catching the user in the instance of asking for new password
def generate_otp():
    uuid_key = shortuuid.uuid()
    unique_key = uuid_key[:6]
    return unique_key






class PasswordResetEmailVerify(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    #funciton for getting user we wanna change the password for 
    def get_object(self):
        email = self.kwargs['email']
        user = User.objects.get(email=email)#catching the user via email inpiuted in frontend 

        if user:
            user.otp = generate_otp()
            user.save() #saving the user instance to the db

            uidb64 = user.pk
            otp = user.otp
            #create link to connect to frontend for reseting password
            link = f"http://localhost:5173/create-new-password?otp={otp}&uidb64={uidb64}"
            print ("link ====", link)


        return user


class PasswordChangeView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    #function for getting user we wanna change the password for 
    def create(self, request, *args, **kwargs):
        payload = request.data

        otp = payload['otp']
        uidb64 = payload['uidb64']
        # reset_token = payload['reset_token']
        password = payload['password']

        user= User.objects.get (otp=otp, id=uidb64)
        if user:
            user.set_password(password)
            user.otp = ""
            # user.reset_token = ""
            user.save()

            return Response({"message" : "Password Changed Successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "As Error Occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ProfileView(generics.RetrieveUpdateAPIView):
    """ API view getting profile for a user"""
    permission_classes = (AllowAny,)
    serializer_class = ProfileSerializer


    def get_object(self):
        user_id = self.kwargs['user_id']
        #get user data from data and grabbing id to use for filter user model and get user instance
        user = User.objects.get(id=user_id)
        #eget profile instance for user
        profile = Profile.objects.get(user=user)

        return profile



