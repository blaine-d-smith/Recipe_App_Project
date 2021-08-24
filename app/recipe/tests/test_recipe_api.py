import os
import tempfile
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from PIL import Image

RECIPES_URL = reverse('recipe:recipe-list')


def recipe_image_url(recipe_id):
    """
    Recipe image URL.
    """
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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
            'password12345*'
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

    def test_create_recipe(self):
        """
        Test for creating recipe.
        """
        payload = {
            'title': 'Key lime pie',
            'prep_time_mins': 10,
            'cook_time_mins': 35,
            'price': 10.50
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_tags(self):
        """
        Test for creating recipe with tags.
        """
        test_tag_1 = create_sample_tag(user=self.user, name='Main Course')
        test_tag_2 = create_sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'New york cheesecake',
            'tags': [test_tag_1.id, test_tag_2.id],
            'prep_time_mins': 10,
            'cook_time_mins': 45,
            'price': 15.00,
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(test_tag_1, tags)
        self.assertIn(test_tag_2, tags)

    def test_create_recipe_ingredients(self):
        """
        Test for creating recipe with ingredients.
        """
        test_ingredient_1 = create_sample_ingredient(
            user=self.user,
            name='Sour cream')
        test_ingredient_2 = create_sample_ingredient(
            user=self.user,
            name='Russet Potato')
        payload = {
            'title': 'Baked potatoes',
            'ingredients': [test_ingredient_1.id, test_ingredient_2.id],
            'prep_time_mins': 5,
            'cook_time_mins': 65,
            'price': 4.00,
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(test_ingredient_1, ingredients)
        self.assertIn(test_ingredient_2, ingredients)

    def test_update_partial_recipe(self):
        """
        Test updating recipes with patch.
        """
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        new_tag = create_sample_tag(user=self.user, name='Sriracha')
        payload = {
            'title': 'Honey Sriracha Chicken',
            'tags': [new_tag.id],
        }
        url = recipe_detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_update_complete_recipe(self):
        """
        Test updating recipes with put.
        """
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        payload = {
            'title': 'Cajun Shrimp and Rice Skillet',
            'prep_time_mins': 10,
            'cook_time_mins': 35,
            'price': 11.00,
        }
        url = recipe_detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.prep_time_mins, payload['prep_time_mins'])
        self.assertEqual(recipe.cook_time_mins, payload['cook_time_mins'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test2@blainesmith.me',
            'password12345'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.recipe = create_sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """
        Test uploading an image to a recipe.
        """
        url = recipe_image_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_400(self):
        """
        Test uploading an invalid image to a recipe.
        """
        url = recipe_image_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
