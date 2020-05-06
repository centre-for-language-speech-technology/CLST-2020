from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from equestria.views import GenericTemplate
from django.views.generic import TemplateView
from django.contrib import messages
from accounts.models import UserProfile
from upload.forms import UploadForm
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

"""Module serving responses to user upon request."""


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
            return redirect("welcome")
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
                return redirect("welcome")
        else:
            # implement error handling here
            messages.info(request, "Invalid username or password")
            return redirect("accounts:login")


class Forgot(TemplateView):
    """Forgot password page."""

    template_name = "accounts/forgot.html"

    def get(self, request, **kwargs):
        """
        GET request for forgot password view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the forgot password page
        """
        print(settings.ADMIN_EMAIL)
        context = {"admin_email": settings.ADMIN_EMAIL}
        return render(request, self.template_name, context)


class Logout(TemplateView):
    """Page to logout."""

    template_name = "accounts/logout.html"

    def get(self, request, *args, **kwargs):
        """
        GET request for logout view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the logout page or a redirect to the next parameter or home page
        """
        next_page = request.GET.get("next")
        if request.user.is_authenticated:
            logout(request)
            if next_page:
                return redirect(next_page)
            return render(request, self.template_name)
        else:
            if next_page:
                return redirect(next_page)
            return redirect("/")


class Settings(LoginRequiredMixin, GenericTemplate):
    """Page to configure user settings."""

    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"

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


class Overview(LoginRequiredMixin, GenericTemplate):
    """Page to display user files and stuff."""

    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"

    template = "accounts/overview.html"

    def get(self, request):
        """Display files."""
        wavForm = UploadForm()
        txtForm = UploadForm()
        context = {
            "WAVform": wavForm,
            "TXTform": txtForm,
        }
        return render(request, self.template, context)
