from rest_framework import serializers
from core.models import Tag


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
