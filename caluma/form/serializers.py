from django.contrib.auth import get_user_model
from rest_framework_json_api import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            get_user_model().REQUIRED_FIELDS + [
                get_user_model().USERNAME_FIELD
            ]
        )
