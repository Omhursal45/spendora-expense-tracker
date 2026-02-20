# expenses/forms.py
from django import forms
from .models import Expense

DEFAULT_CATEGORIES = [
    ('Food', 'Food'),
    ('Transport', 'Transport'),
    ('Shopping', 'Shopping'),
    ('Bills', 'Bills'),
    ('Health', 'Health'),
    ('Entertainment', 'Entertainment'),
    ('Other', 'Other'),
]

class ExpenseForm(forms.ModelForm):
    category = forms.ChoiceField(
        choices=DEFAULT_CATEGORIES,
        required=True,
        initial='Food',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date_created']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'date_created': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
