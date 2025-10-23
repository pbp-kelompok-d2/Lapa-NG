# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import CustomUser, normalize_indonesia_number

digit_validator = RegexValidator(regex=r'^\d+$', message='Phone number must contain only digits.')

class CustomUserCreationForm(UserCreationForm):
    # Extra fields
    name = forms.CharField(max_length=255, required=True)
    role = forms.ChoiceField(choices=CustomUser.ROLES, initial='owner')
    # Use input attributes to hint mobile keyboards and browser validation
    number = forms.CharField(
        max_length=11,
        required=True,
        validators=[digit_validator],
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',   # mobile numeric keyboard
            'pattern': r'\d*',       # simple client-side pattern
            'maxlength': '11',
            'placeholder': '081234567890'
        })
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "name", "role", "number")

    def clean_number(self):
        number = self.cleaned_data.get('number', '').strip()
        # extra checks you might want
        if not number:
            raise forms.ValidationError("Phone number is required.")
        if not number.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return number

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            # normalize the number before saving profile
            raw_number = self.cleaned_data.get('number', '')
            normalized = normalize_indonesia_number(raw_number)

            CustomUser.objects.create(
                user=user,
                name=self.cleaned_data.get('name', ''),
                role=self.cleaned_data.get('role', CustomUser.ROLES[0][0]),
                number=normalized
            )

        return user

