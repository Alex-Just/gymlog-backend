from rest_framework import serializers

from gymlog.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = [
            "username",
            "name",
            "bio",
            "url",
            "language",
            "profile_picture",
            "private_profile",
        ]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"},
        }

    @staticmethod
    def validate_profile_picture(value):
        if value and not hasattr(value, "file"):
            msg = "The submitted data was not a file."
            raise serializers.ValidationError(msg)
        return value
