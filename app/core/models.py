import os
import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)


def recipe_image_filepath(instance, filename):
    """
    Generates filepath for recipe image.
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/recipe/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates a new user model.
        """
        if not email:
            # Raises error if email is None
            raise ValueError('Please enter an email address')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        Creates a new superuser model.
        """
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses email for username.
    """
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """
    Tag model for recipes.
    """
    name = models.CharField(max_length=150)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """
        Provides a readable string representation of Tag object.
        """
        return self.name


class Ingredient(models.Model):
    """
    Ingredient model within recipe.
    """
    name = models.CharField(max_length=150)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """
        Provides a readable string representation of Ingredient object.
        """
        return self.name


class Recipe(models.Model):
    """
    Creates a new Recipe model.
    """
    title = models.CharField(max_length=150)
    image = models.ImageField(null=True, upload_to=recipe_image_filepath)
    prep_time_mins = models.IntegerField()
    cook_time_mins = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    url = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """
        Provides a readable string representation of Recipe object.
        """
        return self.title
