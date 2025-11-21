from django import forms
from .models import Ticket

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('buyer_name', 'buyer_email', 'seat_number')
        widgets = {
            'buyer_name': forms.TextInput(attrs={'placeholder': 'Ваше имя'}),
            'buyer_email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
            'seat_number': forms.TextInput(attrs={'placeholder': 'Номер места (опционально)'}),
        }
