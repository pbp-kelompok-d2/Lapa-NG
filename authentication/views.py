from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, logout

from .forms import CustomUserCreationForm
from .models import CustomUser, normalize_indonesia_number

import datetime

from django.urls import reverse

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the built-in User instance but delay committing related CustomUser creation
            user = form.save(commit=True)

            # Normalize phone number before saving to CustomUser
            raw_number = form.cleaned_data.get('number', '')
            normalized = normalize_indonesia_number(raw_number)

            # Create the CustomUser record linked to the newly created User
            CustomUser.objects.create(
                user=user,
                name=form.cleaned_data.get('name', ''),
                role=form.cleaned_data.get('role', CustomUser.ROLES[0][0]),
                number=normalized
            )

            messages.success(request, "Your account has been successfully created!")
            return redirect(reverse('authentication:login'))
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main"))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response

   else:
      form = AuthenticationForm(request)

   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return redirect('main:login')