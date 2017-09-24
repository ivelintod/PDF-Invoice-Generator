from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils import timezone
from internationalflavor.vat_number import VATNumberField
from internationalflavor.vat_number.validators import VATNumberValidator
from internationalflavor.iban import IBANField
from internationalflavor.iban.validators import IBANValidator
#import uuid
import datetime


alphanumeric_val = RegexValidator(r'^[0-9a-zA-Z,. ]*$',
                                  '''Only alphanumeric
                                     characters are allowed.''')


class Dealer(models.Model):
    address = models.CharField(max_length=50, validators=[alphanumeric_val])
    uic = models.CharField(max_length=25, verbose_name="UIC")
    vat = VATNumberField(countries=['BG'], verbose_name="VAT")
    iban = IBANField(countries=['BG'], verbose_name="IBAN")


class Company(models.Model):
    name = models.CharField(max_length=25, validators=[alphanumeric_val])
    address = models.CharField(max_length=50, validators=[alphanumeric_val])
    owner = models.ForeignKey(Dealer, on_delete=models.CASCADE)


class Bank(models.Model):
    name = models.CharField(max_length=25, validators=[alphanumeric_val])
    client = models.ForeignKey(Dealer, on_delete=models.CASCADE)


class Order(models.Model):
    total_price = models.DecimalField(max_digits=6, decimal_places=2)
    comments = models.TextField(max_length=256)


class Invoice(models.Model):
    #number = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(max_length=8)
    place = models.CharField(max_length=25, validators=[alphanumeric_val])
    date = models.DateTimeField(default=timezone.now)
    payment_due_date = models.DateTimeField()
    order_comments = models.TextField(max_length=150, null=True)
    seller = models.ForeignKey(Dealer, on_delete=models.CASCADE,
                               related_name='invoice_sell')
    buyer = models.ForeignKey(Dealer, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        today = datetime.date.today()
        today_string = today.strftime('%y%m%d')
        next_invoice_number = '01'
        last_invoice = Invoice.objects.filter(number__startswith=today_string)\
                                      .order_by('number').last()
        if last_invoice:
            last_invoice_number = int(last_invoice.number[6:])
            next_invoice_number = '{0:02d}'.format(last_invoice_number + 1)
        self.number = today_string + next_invoice_number

        super().save(*args, **kwargs)


class Item(models.Model):
    name = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    description = models.TextField(max_length=256, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    value = models.DecimalField(max_digits=6, decimal_places=2)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True)
