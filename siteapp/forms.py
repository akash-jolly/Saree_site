# siteapp/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=200)
    phone = forms.CharField(max_length=20)
    address_line1 = forms.CharField(max_length=255, label="Address line 1")
    address_line2 = forms.CharField(
        max_length=255,
        label="Address line 2",
        required=False,
    )
    city = forms.CharField(max_length=100)
    pincode = forms.CharField(max_length=10)

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not (phone.isdigit() and len(phone) == 10):
            raise forms.ValidationError("Enter a valid 10-digit phone number.")
        return phone

    def clean_pincode(self):
        pincode = self.cleaned_data.get("pincode", "").strip()
        if not (pincode.isdigit() and len(pincode) == 6):
            raise forms.ValidationError("Enter a valid 6-digit pincode.")
        return pincode
