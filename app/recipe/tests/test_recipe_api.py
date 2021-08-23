from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def recipe_detail_url(recipe_id):
    """
    Recipe detail URL.
    """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_sample_tag(user, **params):
    """
    Creates a sample tag.
    """
    content = {
        'name': 'Main Course',
    }
    content.update(params)

    return Tag.objects.create(user=user, **content)


def create_sample_ingredient(user, **params):
    """
    Creates a sample ingredient.
    """
    content = {
        'name': 'Kosher salt',
    }
    content.update(params)

    return Ingredient.objects.create(user=user, **content)


def create_sample_recipe(user, **params):
    """
    Creates a sample recipe.
    """
    content = {
        'title': 'Sample Recipe',
        'prep_time_mins': 5,
        'cook_time_mins': 15,
        'price': 20,
    }
    content.update(params)

    return Recipe.objects.create(user=user, **content)


class PublicRecipeAPITests(TestCase):
    """
    Tests the public recipe API.
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Tests if login is required for retrieving recipes.
        """
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRecipesAPITests(TestCase):
    """
    Test the authenticated recipes API.
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@blainesmith.me',
            'password12345'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe_list(self):
        """
        Test if retrieving list of recipes.
        """
        create_sample_recipe(user=self.user)
        create_sample_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)

        recipe = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_for_authenticated_user(self):
        """
        Test if recipes are returned for the authenticated user.
        """
        dummy_user2 = get_user_model().objects.create_user(
            'dummy2@blainesmith.me',
            'testingpassword'
        )
        create_sample_recipe(user=dummy_user2)
        create_sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail_url(self):
        """
        Test for viewing URL of detailed recipe.
        """
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        recipe.ingredients.add(create_sample_ingredient(user=self.user))

        url = recipe_detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
