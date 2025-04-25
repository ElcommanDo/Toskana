from django import forms
from django.forms import modelformset_factory
from .models import Contract, Product

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = '__all__'

ProductFormSet = modelformset_factory(
    Product,
    fields=('product_title', 'total_price', 'notes'),
    extra=15,
    can_delete=True
)
