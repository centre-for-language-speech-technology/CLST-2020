from django import forms

"""Module to creat forms for accounts app."""


class AudioSelectForm(forms.Form):
    """Form to select an audio file."""

    def __init__(self, user, *args, **kwargs):
        """Instantiate form."""
        # user = kwargs.pop('user')
        self.user = user
        super(AudioSelectForm, self).__init__(*args, **kwargs)

    files = forms.ModelChoiceField(queryset=None, widget=forms.Select())
