from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:profile')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """
    Test the public user API.
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_successful(self):
        """
        Test creating user is successful.
        """
        payload = {
            'email': 'test@blainesmith.me',
            'password': 'password12345',
            'name': 'Jon Snow',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        # Ensures password is not returned
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """
        Tests if user already exists when creating new user.
        """
        payload = {
            'email': 'test@blainesmith.me',
            'password': 'password12345',
            'name': 'Jon Snow',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_length(self):
        """
        Tests if password is > 8 characters.
        """
        payload = {
            'email': 'test@blainesmith.me',
            'password': 'pass',
            'name': 'Jon Snow',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_user_token(self):
        """
        Tests if a token is created for a user.
        """
        payload = {
            'email': 'test@blainesmith.me',
            'password': 'password12345',
            'name': 'Jon Snow',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """
        Tests if token is created with invalid credentials.
        """
        create_user(email='test@blainesmith.me', password='password12345')
        payload = {
            'email': 'test@blainesmith.me',
            'password': 'incorrect',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Tests if token is created if user does not exist.
        """
        payload = {
            'email': 'test@blainesmith.me',
            'password': 'password12345',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """
        Tests if email and password required.
        """
        payload = {
            'email': 'test@blainesmith.me',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """
        Tests that authentication is required for user.
        """
        res = self.client.post(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserAPITests(TestCase):
    """
    Test the authenticated user API.
    """

    def setUp(self):
        """Dummy user for testing."""
        self.user = create_user(
            email='test@blainesmith.me',
            password='password12345',
            name='Jon Snow'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_successful(self):
        """
        Tests if profile is returned for logged in user.
        """
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_profile_not_allowed(self):
        """
        Tests that POST is not allowed for Profile URL.
        """
        res = self.client.post(PROFILE_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """
        Test updating of profile for authenticated user.
        """
        payload = {
            'name': 'New Name',
            'password': 'newpassword12345',
        }
        res = self.client.patch(PROFILE_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
