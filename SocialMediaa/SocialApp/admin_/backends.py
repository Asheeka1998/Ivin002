from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from .models import Users


class MyCustomAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(username=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            pass

        try:
            user = Users.objects.get(user=username)
            if user.password == password:
                return user
        except Users.DoesNotExist:
            pass

        return None
