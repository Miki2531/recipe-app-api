""" 
Test for user API.
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import UserSerializer, AuthTokenSerializer

class CreateUserView(generics.CreateAPIView):
    """ Create a new user in the system. """
    serializer_class  = UserSerializer

class createTokenView(ObtainAuthToken):
    """ Create a new token for user."""
    serializer_class = AuthTokenSerializer
    serializer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """ Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]

    """Allows access only to authenticated users."""
    permission_classes = [permissions.IsAuthenticated]

