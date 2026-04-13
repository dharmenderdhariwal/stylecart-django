from django import forms

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    address = forms.CharField(max_length=255)
    city = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
