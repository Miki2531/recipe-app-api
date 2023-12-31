"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    """ Create and return a new user."""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """ Test the public feature of user api."""

    def setUp(self):
        self.client = APIClient() 

    def test_create_user_success(self):
        """ Test creating a user is successfull."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',

        }
        res  = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_email_exists_error(self):
        """ Test error returned if user with email exists."""
        payload = {
            'email':'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """ Test an error is returned if password less than s chars."""

        payload = {
            'email':'test@example.com',
            'password':'pw',
            'name': ' Test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email = payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ Test generate token for valid credentials."""
        user_details ={
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test_user_password123',
        }

        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """ Test return a bad request if credentials is invalid."""
        create_user(email='test@example.com', password='badpass')
        payload ={
            'email': 'test@example.com', 'password': 'badpass'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_email_not_found(self):
        """ Test error returned if user not found for given email."""
        payload = {'email': 'test@example.com', 'pasword':'pass123'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_token_blank_password(self):
        """ Test error returned if the user posting password blank"""

        payload = {'email':'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_retrive_user_unauthorized(self):
        """ Test authentication is required for users."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """ Test API request that require authentication"""

    def setUp(self):
        self.user = create_user(
            email = 'test@example.com',
            password = 'testpass123',
            name = 'Test Name'
        )

        self.client = APIClient()
        """ Forcibly authenticates outgoing requests with the given user and/or token."""
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """ Test retrieving profile for logged user"""

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_not_allowed(self):
        """ Test POST is not allowed for the me endpoint"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ Test updating the user profile for authenticated user."""
        payload = {
            'name': 'Update name', 'password': 'newpassword123'
        }

        """Send a resource to the server using PATCH."""
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)



