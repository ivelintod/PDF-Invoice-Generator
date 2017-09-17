from django.conf.urls import url

from .views import index, invoices, pdf_single_invoice, pdf_multiple_in_one_day_invoices

namespace = "inv_gen"

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^invoices/$', invoices, name="invoices"),
    url(r'^pdf-single/(?P<number>[0-9]+)/$', pdf_single_invoice,
        name="pdf_single_invoice"),
    url(r'^pdf-multi/(?P<number>[0-9]+)/$',
        pdf_multiple_in_one_day_invoices,
        name="pdf_multiple_in_one_day_invoices"),
]
