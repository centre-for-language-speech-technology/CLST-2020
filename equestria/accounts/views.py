from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.views.generic import TemplateView
from django.contrib import messages
from django.conf import settings
from .forms import UserUpdateForm


class Signup(TemplateView):
    """Page to create new account."""

    template = "accounts/signup.html"

    def get(self, request, **kwargs):
        """Render django user creation form."""
        form = UserCreationForm()
        return render(request, self.template, {"form": form})

    def post(self, request, **kwargs):
        """Validate form, create new user account, login user, redirect to main page."""
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            #  log in the user
            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            return redirect("welcome")
        else:
            # implement error handling here
            messages.info(
                request,
                "Invalid password or already taken user name. Please check the requirements for passwords",
            )
            return redirect("accounts:signup")


class Login(TemplateView):
    """Page to login as existing user."""

    template = "accounts/login.html"

    def get(self, request, **kwargs):
        """Render django user login form."""
        form = AuthenticationForm()
        return render(request, self.template, {"form": form})

    def post(self, request, **kwargs):
        """Validate form, login user, redirect."""
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # log the user in
            user = form.get_user()
            login(request, user)
            if "next" in request.POST:
                return redirect(request.POST.get("next"))
            else:
                return redirect("projects:overview")
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
        context = {"admin_email": settings.ADMIN_EMAIL}
        return render(request, self.template_name, context)


class Logout(TemplateView):
    """Page to logout."""

    template_name = "accounts/logout.html"

    def get(self, request, **kwargs):
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


class ChangePasswordView(LoginRequiredMixin, TemplateView):
    """Account details page, requires logged in user."""

    template_name = "accounts/password.html"

    def get(self, request, **kwargs):
        """
        GET method for account details page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the accounts page with initial information filled in
        """
        form = UserUpdateForm()

        context = {"form": form}

        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """
        POST method for account details page.

        Changes details of a user account
        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the accounts page
        """
        form = UserUpdateForm(request.POST)

        context = {"form": form}

        if form.is_valid():
            if request.user.check_password(
                form.cleaned_data.get("oldpassword")
            ):
                request.user.set_password(form.cleaned_data.get("password"))
                request.user.save()
                context["succeeded"] = True
                return render(request, self.template_name, context)
            else:
                context["failed"] = True
                return render(request, self.template_name, context)

        return render(request, self.template_name, context)
