from django import forms


class UserUpdateForm(forms.Form):
    """Update user information form."""

    oldpassword = forms.CharField(
        widget=forms.PasswordInput, label="Old password"
    )
    password = forms.CharField(widget=forms.PasswordInput, label="New password")
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Repeat new password"
    )

    def clean(self):
        """
        Check if two passwords are the same and if the old password is not equal to the new password.

        :return: the cleaned data
        """
        cleaned_data = super(UserUpdateForm, self).clean()
        if cleaned_data.get("password") != cleaned_data.get("password2"):
            raise forms.ValidationError("The new passwords do not match.")
        elif cleaned_data.get("password") == cleaned_data.get("oldpassword"):
            raise forms.ValidationError(
                "The new password needs to be different from the old one."
            )

        return cleaned_data
