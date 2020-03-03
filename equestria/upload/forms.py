from django import forms
from.formExtension import ExtFileField


class UploadTXTForm(forms.Form):
    txtFile = ExtFileField(ext_whitelist=('.txt', '.txt'), widget=forms.FileInput(
        attrs={'class': 'custom-file-input'}))
    # need dublicate in whitelist otherwise string will be treated as list and only valid filetypes are ".","t","x" which does not make sense


class UploadWAVForm(forms.Form):
    wavFile = ExtFileField(ext_whitelist=('.wav', '.wav'), widget=forms.FileInput(
        attrs={'class': 'custom-file-input'}))
    # need dublicate in whitelist otherwise string will be treated as list and only valid filetypes are ".","w","a","v" which does not make sense


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    f = forms.FileField()
