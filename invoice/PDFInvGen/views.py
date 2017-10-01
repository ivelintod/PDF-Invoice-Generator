from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.forms.formsets import formset_factory
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import os
from weasyprint import HTML, CSS
from .models import Item, Dealer, Invoice, Company, Bank
from .forms import DealerForm, CompanyForm, BankForm, ItemForm, InvoiceForm,\
    BaseItemFormSet


CSS_FILE = os.path.join(settings.BASE_DIR,
                        'static/PDFInvGen/css/invoice.css')

BOOTSTRAP_FILE = os.path.join(settings.BASE_DIR,
                              'static/PDFInvGen/css/bootstrap.css')


def get_invoice_details(inv_number):
    invoice = get_object_or_404(Invoice, number=inv_number)
    seller = invoice.seller
    seller_company = seller.company_set.last()
    seller_bank = seller.bank_set.last()
    buyer = invoice.buyer
    buyer_company = buyer.company_set.last()
    buyer_bank = buyer.bank_set.last()
    items = invoice.item_set.all()
    return locals()


def index(request):
    ItemFormSet = formset_factory(ItemForm, formset=BaseItemFormSet)

    if request.method == "POST":
        seller_form = DealerForm(request.POST, prefix="seller")
        company_form = CompanyForm(request.POST, prefix="company")
        bank_form = BankForm(request.POST, prefix="bank")
        item_formset = ItemFormSet(request.POST, prefix="item")
        invoice_form = InvoiceForm(request.POST, prefix="invoice")
        if seller_form.is_valid() and company_form.is_valid()\
           and bank_form.is_valid() and item_formset.is_valid()\
           and invoice_form.is_valid():

            try:
                seller = Dealer.objects.get(iban=seller_form.cleaned_data['iban'])
            except Dealer.DoesNotExist:
                seller = seller_form.save(commit=False)
                seller.iban = seller_form.cleaned_data['iban']
                seller.vat = seller_form.cleaned_data['vat']
                seller.save()

            try:
                company_name = company_form.cleaned_data['name']
                company = Company.objects.get(name=company_name, owner=seller)
            except Company.DoesNotExist:
                company = company_form.save(commit=False)
                company.owner = seller
                company.save()

            try:
                bank_name = company_form.cleaned_data['name']
                bank = Bank.objects.get(name=bank_name, client=seller)
            except Bank.DoesNotExist:
                bank = bank_form.save(commit=False)
                bank.client = seller
                bank.save()

            invoice = invoice_form.save(commit=False)
            invoice.seller = seller
            invoice.buyer = Dealer.objects.get(pk=1)
            invoice.save()

            items = []
            for item_form in item_formset:
                name = item_form.cleaned_data['name']
                description = item_form.cleaned_data['description']
                quantity = item_form.cleaned_data['quantity']
                price = item_form.cleaned_data['price']
                value = int(quantity) * int(price)
                items.append(Item(name=name, description=description,
                                  quantity=quantity, price=price,
                                  value=value, invoice=invoice))
            Item.objects.bulk_create(items)
            print('formichkite', item_formset)
            messages.success(request, "You have successfully submitted invoice information!")

    else:
        seller_form = DealerForm(prefix='seller')
        company_form = CompanyForm(prefix='company')
        bank_form = BankForm(prefix='bank')
        item_formset = ItemFormSet(prefix='item')
        invoice_form = InvoiceForm(prefix="invoice")

    return render(request, 'PDFInvGen/index.html',
                  {'forms': [('Seller', seller_form),
                             ('Company', company_form),
                             ('Bank', bank_form),
                             ('Items', item_formset),
                             ('Invoice Details', invoice_form)],
                   'formset_len': len(item_formset)})


def invoices(request):
    all_invoices = Invoice.objects.all()
    return render(request, 'PDFInvGen/invoices.html', {'invoices': all_invoices})


def pdf_single_invoice(request, number):
    invoice_details = get_invoice_details(number)
    order_price = sum(item.value for item in invoice_details['items'])
    total_order_price = 0.2 * float(order_price) + float(order_price)
    invoice_details.update({'total_order_price': total_order_price})
    template_str = render_to_string('PDFInvGen/base_invoice.html',
                                    invoice_details)
    html = HTML(string=template_str)
    html.write_pdf(target='/tmp/invoice.pdf',
                   stylesheets=[CSS(filename=CSS_FILE),
                                CSS(filename=BOOTSTRAP_FILE)])

    fs = FileSystemStorage('/tmp')
    with fs.open('invoice.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attatchement; filename="invoice.pdf"'
        return response
    #return render(request, 'PDFInvGen/base_invoice.html', invoice_details)


def pdf_multiple_in_one_day_invoices(request, number):
    invoice_details = get_invoice_details(number)
    temp_invoices = Invoice.objects.filter(date__date=invoice_details['invoice'].date.date())
    seller_company_to_check = Company.objects.filter(owner=invoice_details['seller']).last()
    buyer_company_to_check = Company.objects.filter(owner=invoice_details['buyer']).last()
    related_invoices = []
    for inv in temp_invoices:
        candidate = get_invoice_details(inv.number)
        if invoice_details['seller_company'] == candidate['seller_company']\
            and invoice_details['buyer_company'] == candidate['buyer_company']:
            related_invoices.append(inv)

    #related_invoices = (inv for inv in temp_invoices if
    #                    seller_company_to_check == invoice_details['seller_company']
    #                    and buyer_company_to_check == invoice_details['buyer_company'])

    for invoice in related_invoices:
        invoice_details['items'] = invoice_details['items'] | invoice.item_set.all()

    order_price = sum((item.value for item in invoice_details['items']))
    total_order_price = 0.2 * float(order_price) + float(order_price)
    invoice_details.update({'total_order_price': total_order_price})
    template_str = render_to_string('PDFInvGen/base_invoice.html',
                                    invoice_details)
    html = HTML(string=template_str)
    html.write_pdf(target='/tmp/invoice.pdf',
                   stylesheets=[CSS(filename=CSS_FILE),
                                CSS(filename=BOOTSTRAP_FILE)])

    fs = FileSystemStorage('/tmp')
    with fs.open('invoice.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attatchement; filename="invoice.pdf"'
        return response
    #return render(request, 'PDFInvGen/base_invoice.html', invoice_details)
