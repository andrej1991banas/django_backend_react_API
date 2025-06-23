from rest_framework import serializers
from .models import User, Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """"""
    @classmethod
    # Define a custom method to get the token for a user
    def get_token(cls, user):
        # Call the parent class's get_token method
        token = super().get_token(user)

        # Add custom claims to the token
        token['fullname'] = user.fullname
        token['email'] = user.email
        token['username'] = user.username
        #i can define what data can token inscripted for future use
        try:
            token['vendor_id'] = user.vendor.id
        except:
            token['vendor_id'] = 0

        # Return the token with custom claims
        return token


class RegisterSerializer(serializers.ModelSerializer):
    # Define fields for the serializer, including password and password2
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        # Specify the model that this serializer is associated with
        model = User
        # Define the fields from the model that should be included in the serializer for User creation/registration
        fields = ('fullname', 'email', 'mobile', 'password', 'password2')

    def validate(self, attrs):
        # Define a validation method to check if the passwords match
        if attrs['password'] != attrs['password2']:
            # Raise a validation error if the passwords don't match
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # Return the validated attributes
        return attrs

# If the validate function go through I have validated data in instance of the user and then
    #can continue to crate a User with validated data provide as instance of the User
    def create(self, validated_data):
        # Define a method to create a new user based on validated data
        user = User.objects.create(
            fullname=validated_data['fullname'],
            email=validated_data['email'],
            mobile=validated_data['mobile']
        )
        email_username, mobile = user.email.split('@')
        user.username = email_username

        # Set the user's password based on the validated data
        user.set_password(validated_data['password'])
        user.save()

        # Return the created user
        return user






class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(ProfileSerializer, self).__init__(*args, **kwargs)
    #     # Customize serialization depth based on the request method.
    #     request = self.context.get('request')
    #     if request and request.method == 'POST':
    #         # When creating a new product FAQ, set serialization depth to 0.
    #         self.Meta.depth = 0
    #     else:
    #         # For other methods, set serialization depth to 3.
    #         self.Meta.depth = 3

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = UserSerializer(instance.user).data
        return response
