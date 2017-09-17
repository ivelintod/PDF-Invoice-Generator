from django import forms
from django.forms.formsets import BaseFormSet
from internationalflavor.vat_number.forms import VATNumberFormField
from internationalflavor.iban.forms import IBANFormField
from .models import Invoice, Dealer, Order, Company, Bank, Item


class DealerForm(forms.ModelForm):

    vat = VATNumberFormField(countries=['BG'])
    iban = IBANFormField(countries=['BG'])

    class Meta:
        model = Dealer
        fields = ('address', 'uic', 'vat', 'iban')

        help_texts = {
            'vat': ("Hmmmmmmm")
        }

        error_messages = {
            'vat': {
                'invalid': ("Invalid VAT format."),
            },
        }


class CompanyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ('name', 'address',)


class BankForm(forms.ModelForm):

    class Meta:
        model = Bank
        fields = ('name',)


class ItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ('name', 'description', 'quantity', 'price',)


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('total_price', 'comments',)


class InvoiceForm(forms.ModelForm):

    class Meta:
        model = Invoice
        fields = ('place', 'date', 'payment_due_date', 'order_comments')


class BaseItemFormSet(BaseFormSet):

    def clean(self):
        "Validation to check against repetitive items"

        if any(self.errors):
            return

        names = []
        duplication = False

        for form in self.forms:
            if form.cleaned_data:
                name = form.cleaned_data['name']
                if name in names:
                    duplication = True

            if duplication:
                raise forms.ValidationError(
                    "Item names must be unique",
                    code="duplicate_names"
                )
