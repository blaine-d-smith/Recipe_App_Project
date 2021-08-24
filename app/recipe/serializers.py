from rest_framework import serializers
from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """
    Serializes and deserializes tag instances into representations(JSON).
    """

    class Meta:
        """
        Fields of tag instances that will get serialized/deserialized.
        """
        model = Tag
        fields = (
            'id',
            'name',
        )
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializes and deserializes ingredient instances
    into representations(JSON).
    """

    class Meta:
        """
        Fields of ingredient instances that will get serialized/deserialized.
        """
        model = Ingredient
        fields = (
            'id',
            'name',
        )
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializes and deserializes recipe instances
    into representations(JSON).
    """
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        """
        Fields of recipe instances that will get serialized/deserialized.
        """
        model = Recipe
        fields = (
            'id',
            'title',
            'ingredients',
            'tags',
            'prep_time_mins',
            'cook_time_mins',
            'price',
            'url',
        )
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializes and deserializes recipe detail
    instances into representations(JSON).
    """
    ingredients = IngredientSerializer(
        many=True,
        read_only=True
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )


class RecipeImageSerializer(serializers.ModelSerializer):
    """
    Serializes and deserializes recipe image
    instances into representations(JSON).
    """

    class Meta:
        model = Recipe
        fields = (
            'id',
            'image',
        )
        read_only_fields = ('id',)
