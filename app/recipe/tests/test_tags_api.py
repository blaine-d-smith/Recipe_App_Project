from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsAPITests(TestCase):
    """
    Tests the public tags API.
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Tests if login is required for retrieving tags.
        """
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTagsAPITests(TestCase):
    """
    Test the authenticated tags API.
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@blainesmith.me',
            'password12345'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """
        Test if retrieving tags.
        """
        Tag.objects.create(user=self.user, name='Seafood')
        Tag.objects.create(user=self.user, name='BBQ')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_for_authenticated_user(self):
        """
        Test if tags are returned for the authenticated user.
        """
        dummy_user2 = get_user_model().objects.create_user(
            'dummy2@blainesmith.me',
            'testingpassword'
        )
        Tag.objects.create(user=dummy_user2, name='Pasta')
        tag = Tag.objects.create(user=self.user, name='Side Dishes')
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
