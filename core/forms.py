from django import forms
from .data import PROVINCES

PAYMENT_METHODS = (
    ('ip', 'idpay'),
    ('zp','zarinpal')
    )

class CheckOutForm(forms.Form):
    province = forms.ChoiceField(choices=PROVINCES, required=False, widget=forms.Select(attrs={
        'class':'custom-select d-block w-100',
        'id':'province',
        'name':'province',
        }))
    
    city = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={
        'id':'city',
        'name':'city',
        'class':'form-control',
        'placeholder':'Your city name'
    }))

    postal_code = forms.CharField(max_length=50,required=False ,widget=forms.TextInput(attrs={
        'id':'postal-code',
        'name':'postal-code',
        'class':'form-control',
        'placeholder':'Your postal code'       
    }))

    full_address = forms.CharField(max_length=250,required=False , widget=forms.TextInput(attrs={
        'id':'full-address',
        'name':'full-address',
        'class':'form-control',
        'placeholder':'Enter your full Address'   
    }))

    payment_method = forms.ChoiceField(choices=PAYMENT_METHODS, widget=forms.RadioSelect(attrs={
        'class':'custom-radio',
        'id':'payment-method',
        'name':'payment-method'
    }))


class RefundForm(forms.Form):
    order_id = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'id':'order_id'
    }))

    title = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'id':'title'
    }))

    reason = forms.CharField(max_length=250, widget=forms.Textarea(attrs={
        'id':'reason',
        'rows':3,
    }))
