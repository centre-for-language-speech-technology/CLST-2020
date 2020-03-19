from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from fancybar.views import GenericTemplate
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.contrib import messages


class Signup(GenericTemplate):
    """Page to create new account."""

    template = "accounts/signup.html"

    def get(self, request):
        """Render django user creation form."""
        form = UserCreationForm()
        return render(request, self.template, {"form": form})

    def post(self, request):
        """Validate form, create new user account, login user, redirect to main page."""
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            #  log in the user
            login(request, user)
            return redirect("fancybar:fancybar")
        else:
            # implement error handling here
            messages.info(
                request,
                "Invalid password or already taken user name. Please check the requirements for passwords",
            )
            return redirect("accounts:signup")


class Login(GenericTemplate):
    """Page to login as existing user."""

    template = "accounts/login.html"

    def get(self, request):
        """Render django user login form."""
        form = AuthenticationForm()
        return render(request, self.template, {"form": form})

    def post(self, request):
        """Validate form, login user, redirect."""
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # log the user in
            user = form.get_user()
            login(request, user)
            if "next" in request.POST:
                return redirect(request.POST.get("next"))
            else:
                return redirect("fancybar:fancybar")
        else:
            # implement error handling here
            messages.info(request, "Invalid username or password")
            return redirect("accounts:login")


class Logout(TemplateView):
    """Page to logout."""

    def post(self, request):
        """Logout user, redirect."""
        logout(request)
        return redirect("fancybar:fancybar")
