from django import forms
from .models import User


class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"required": True}),
            "email": forms.EmailInput(attrs={"required": True}),
        }
