from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'description']


class UserCreationFormCustom(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']