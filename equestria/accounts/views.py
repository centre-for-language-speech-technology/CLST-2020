from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from fancybar.views import GenericTemplate
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.contrib import messages
from accounts.models import UserProfile


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


class Settings(GenericTemplate):
    """Page to configure user settings."""

    template = "accounts/settings.html"

    def __get_profile(self, request):
        """Retrieve profile based on user in request."""
        user_profile = (
            UserProfile.objects.select_related()
            .filter(user_id=request.user.id)
            .first()
        )
        return user_profile

    def get(self, request):
        """Display settings."""
        arg = {"profile": self.__get_profile(request)}
        return render(request, self.template, arg)

    def post(self, request):
        """Update settings."""
        user_profile = self.__get_profile(request)
        # Too lazy to sanitize and themes/colors are really someone elses job
        user_profile.favorite_pony = request.POST.get(
            "pony", user_profile.favorite_pony
        )
        user_profile.theme = request.POST.get("theme", user_profile.theme)
        user_profile.background_color = "#" + request.POST.get(
            "background_color", user_profile.background_color
        )
        user_profile.background_lighter = "#" + request.POST.get(
            "background_lighter", user_profile.background_lighter
        )
        user_profile.accent_color = "#" + request.POST.get(
            "accent_color", user_profile.accent_color
        )
        user_profile.accent_darker = "#" + request.POST.get(
            "accent_darker", user_profile.accent_darker
        )
        user_profile.text_color = "#" + request.POST.get(
            "text_color", user_profile.text_color
        )
        user_profile.save()

        arg = {"profile": user_profile}
        return render(request, self.template, arg)
