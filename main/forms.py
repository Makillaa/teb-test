from django import forms
from django.contrib.auth.forms import AuthenticationForm


class EmailAuthenticationForm(AuthenticationForm):
    email = forms.CharField(label="Email", max_length=30,
                               widget=forms.EmailInput(attrs={'class': 'form-control', 'name': 'email'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = forms.HiddenInput()
        self.fields.pop('username', None)
        self.fields.update({
            'email': forms.CharField(label="Email", max_length=30,
                               widget=forms.EmailInput(attrs={'class': 'form-control', 'name': 'email'})),
            'password': forms.CharField(label="Password", max_length=30,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password'})),
        })

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['username'] = cleaned_data.get('email')
        return cleaned_data

    class Meta:
        fields = ['email', 'password']
