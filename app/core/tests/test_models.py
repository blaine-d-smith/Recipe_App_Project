from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def dummy_user(email='dummy@blainesmith.me', password='password12345'):
    """
    Create dummy user.
    """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """
        Test creating a new user with email is successful
        """
        email = 'test@blainesmith.me'
        password = 'password12345'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        Test the email of a new user is normalized
        """
        email = 'test@BLAINESMITH.ME'
        user = get_user_model().objects.create_user(
            email,
            'password12345'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """
        Test creating a new user without email raises error.
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                None,
                'password12345'
            )

    def test_create_new_superuser(self):
        """
        Test creating a new superuser
        """
        user = get_user_model().objects.create_superuser(
            'test@blainesmith.me',
            'password12345'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """
        Tests the tag string representation.
        """
        tag = models.Tag.objects.create(
            user=dummy_user(),
            name='Dummy'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """
        Tests the ingredient string representation.
        """
        ingredient = models.Ingredient.objects.create(
            user=dummy_user(),
            name='Sugar'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """
        Tests the recipe string representation.
        """
        recipe = models.Recipe.objects.create(
            user=dummy_user(),
            title='Tomahawk Ribeye Steak',
            prep_time_mins=5,
            cook_time_mins=45,
            price=34.90
        )

        self.assertEqual(str(recipe), recipe.title)
