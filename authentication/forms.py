# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, URLValidator
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

    profile_picture = forms.URLField(
        required=False,
        validators=[URLValidator()],
        widget=forms.URLInput(attrs={
            'placeholder': 'https://example.com/avatar.jpg',
            'class': 'w-full ...',
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
                number=normalized,
                profile_picture=self.cleaned_data.get('profile_picture') or None
            )

        return user
    
class ProfileForm(forms.ModelForm):
    # include username from the built-in User model
    username = forms.CharField(max_length=150, required=True, label="Username")

    class Meta:
        model = CustomUser
        # role intentionally excluded so users cannot change it
        fields = ['name', 'number', 'profile_picture']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        base_attrs = {
            'class': 'w-full px-4 py-3 border border-gray-300 rounded focus:outline-none focus:border-green-500 transition duration-200',
        }

        # widgets / placeholders
        self.fields['username'].widget.attrs.update({**base_attrs, 'placeholder': 'Username'})
        self.fields['name'].widget.attrs.update({**base_attrs, 'placeholder': 'Full name'})
        self.fields['number'].widget.attrs.update({
            **base_attrs,
            'placeholder': '081234567890',
            'inputmode': 'numeric',
            'pattern': r'\d*',
            'maxlength': '15'
        })
        self.fields['profile_picture'].widget.attrs.update({**base_attrs, 'placeholder': 'https://...'})

        # initial username from related User object
        if instance and getattr(instance, 'user', None):
            self.fields['username'].initial = instance.user.username

        # add validator for number field
        self.fields['number'].validators.append(digit_validator)

    def clean_number(self):
        number = self.cleaned_data.get('number', '').strip()
        if not number:
            raise forms.ValidationError("Phone number is required.")
        if not number.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return number

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if self.instance and getattr(self.instance, 'user', None):
            current_user = self.instance.user
            if User.objects.exclude(pk=current_user.pk).filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        custom = super().save(commit=False)
        username = self.cleaned_data.get('username')

        # update linked User
        if getattr(custom, 'user_id', None):
            user = custom.user
            user.username = username
            if commit:
                user.save()
        else:
            user = User.objects.create(username=username)
            custom.user = user

        if commit:
            custom.save()
        return custom

