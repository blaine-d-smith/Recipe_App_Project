from rest_framework import mixins, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Ingredient, Recipe
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeDetailSerializer)


class BaseRecipeViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    """
    Viewset for recipe attributes.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Retrieves all objects associated with the authenticated user.
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """
        Creates a new recipe.
        """
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeViewSet):
    """
    Viewset for displaying active tag data as JSON.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    # Retrieves active tags.
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseRecipeViewSet):
    """
    Viewset for displaying active ingredient data as JSON.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    # Retrieves active ingredients.
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Viewset for displaying active recipe data as JSON.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    # Retrieves active recipes.
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_queryset(self):
        """
        Retrieves all recipe objects associated for the authenticated user.
        """
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """
        Return serializer class.
        """
        if self.action == 'retrieve':
            return RecipeDetailSerializer

        return self.serializer_class
