""" 
Serializers for user API View.
"""
from django.contrib.auth import (
    get_user_model, 
    authenticate,
    )

from django.utils.translation import gettext as _
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the user object."""
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length':5}}
    def create(self, validated_data):
        """ Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)
    
    def upadate(self, instance, validated_data):
        """ Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            if len(password) < 8:
                  raise serializers.ValidationError("Password must be at least 8 characters long.")
            user.set_password(password)
            user.save()
        return user
    
class AuthTokenSerializer(serializers.Serializer):
        """ Serializer for the user auth token."""
        email = serializers.EmailField()
        password = serializers.CharField(
            style = {'input_type': 'password'},
            trim_whitspace = False,
        )

        def validate(self, attrs):
            """Validate and authenticate the user."""
            email = attrs.get('email')
            password = attrs.get('password')
            """If the given credentials are valid, return a User object."""
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password,

            )
            if not user:
                 msg= _('Unable to authenticate with the provided credentials.')
                 raise serializers.ValidationError(msg, code='authorization')
            attrs['user'] = user
            return attrs