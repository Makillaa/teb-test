from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models


class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user


class TelegramProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='user')
    first_name = models.CharField(max_length=100, null=True, blank=False)
    username = models.CharField(max_length=100, null=True, blank=False)
    photo = models.BinaryField(blank=False, null=True, editable=False)
