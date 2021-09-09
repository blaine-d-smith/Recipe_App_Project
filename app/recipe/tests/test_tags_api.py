from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag, Recipe
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

    def test_create_tag_successful(self):
        """
        Test creating tag is successful.
        """
        payload = {
            'name': 'Dummy tag'
        }
        self.client.post(TAGS_URL, payload)

        # Test fails if exists
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """
        Test creating tag with invalid data.
        """
        payload = {
            'name': ''
        }
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_from_recipes(self):
        """
        Test filtering tags that are assigned
        to recipes.
        """
        tag1 = Tag.objects.create(user=self.user, name='Shrimp')
        tag2 = Tag.objects.create(user=self.user, name='Cajun')
        recipe = Recipe.objects.create(
            title='Cajun Shrimp and Rice Skillet',
            prep_time_mins=10,
            cook_time_mins=35,
            price=11.00,
            user=self.user
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """
        Test filtering tags return unique
        items.
        """
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Steak')
        recipe1 = Recipe.objects.create(
            title='Buttermilk Pancakes',
            prep_time_mins=10,
            cook_time_mins=15,
            price=11.00,
            user=self.user
        )
        recipe1.tags.add(tag)

        recipe2 = Recipe.objects.create(
            title='Ribeye Steak',
            prep_time_mins=30,
            cook_time_mins=25,
            price=25.00,
            user=self.user
        )
        recipe2.tags.add(tag)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
