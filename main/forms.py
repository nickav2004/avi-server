from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, DataTable


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description"]


# below is AVI


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="CSV File")
    description = forms.CharField(required=False)
