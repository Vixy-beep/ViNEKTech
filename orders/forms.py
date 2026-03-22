from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=180)
    email = forms.EmailField()
    phone = forms.CharField(max_length=40)
    shipping_address = forms.CharField(max_length=220)
    city = forms.CharField(max_length=120)
    country = forms.CharField(max_length=120, initial='República Dominicana')
    shipping_zone = forms.ChoiceField(
        choices=[
            ('santo_domingo', 'Santo Domingo'),
            ('interior', 'Interior del pais'),
            ('international', 'Internacional'),
        ],
        initial='santo_domingo',
    )
    coupon_code = forms.CharField(max_length=40, required=False)
    declaration_accepted = forms.BooleanField(required=False)

    def __init__(self, *args, requires_declaration=False, **kwargs):
        self.requires_declaration = requires_declaration
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.requires_declaration and not cleaned_data.get('declaration_accepted'):
            raise forms.ValidationError('Debes aceptar la declaración de uso para continuar con este pedido.')
        return cleaned_data