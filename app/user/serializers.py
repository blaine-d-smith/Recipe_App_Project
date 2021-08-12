from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Serializes and deserializes user instances into representations(JSON).
    """

    class Meta:
        """
        Fields of user instances that will get serialized/deserialized.
        """
        model = get_user_model()
        fields = (
            'email',
            'password',
            'name',
        )
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8}
        }

    def create(self, validated_data):
        """
        Create a new user with password and return it.
        """
        return get_user_model().objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializes and deserializes user authentication
    instances into representations(JSON).
    """
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """
        Authenticates the user.
        """
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Cannot authenticate with credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
