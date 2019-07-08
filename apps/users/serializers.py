from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import exceptions, serializers, validators


User = get_user_model()


class UserSerializer(serializers.Serializer):

    id = serializers.ReadOnlyField()
    email = serializers.EmailField(
        max_length=128,
        validators=[
            validators.UniqueValidator(
                queryset=get_user_model().objects.all(),
                message="A user with that e-mail already exists.",
            )
        ],
    )
    first_name = serializers.CharField(max_length=128, allow_blank=True)
    last_name = serializers.CharField(max_length=128, allow_blank=True)
    theme = serializers.ChoiceField(
        choices=User.THEME_CHOICES, default=User.THEME_DEFAULT
    )

    def update(self, instance, validated_data):
        return User.objects.update(instance, **validated_data)


class UserPasswordChangeSerializer(serializers.Serializer):

    email = serializers.EmailField(max_length=128)
    password = serializers.CharField(max_length=128)
    password_new = serializers.CharField(max_length=128)
    password_confirm = serializers.CharField(max_length=128)

    def validate(self, data):

        email = data.get("email")
        password = data.get("password")
        password_new = data.get("password_new")
        password_confirm = data.get("password_confirm")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise validators.ValidationError("Invalid e-mail/password combination.")

        if not user.check_password(password):
            raise validators.ValidationError("Invalid e-mail/password combination.")

        if password_new != password_confirm:
            raise validators.ValidationError("Passwords do not match.")

        try:
            validate_password(password=password_new, user=user)
        except exceptions.ValidationError:
            raise

        data["user"] = user

        return data

    def create(self, validated_data):

        user = validated_data.get("user")
        password = validated_data.get("password_new")

        user.set_password(password)
        user.save()

        return user
