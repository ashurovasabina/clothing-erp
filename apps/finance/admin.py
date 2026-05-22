from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from apps.core.admin import BaseAdmin
from .models import Invoice, Payment, Expense
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, F, Value, DecimalField


@admin.register(Invoice)
class InvoiceAdmin(BaseAdmin):
    list_display = ('number', 'entity_name', 'invoice_type_display', 'issue_date', 'due_date',
                    'total', 'paid_amount', 'balance', 'status_display')
    list_filter = ('status', 'invoice_type', 'issue_date')
    search_fields = ('number', 'customer__name', 'supplier__name')
    readonly_fields = ('paid_amount',)
    autocomplete_fields = ['customer', 'supplier', 'order', 'purchase_order', 'currency']
    date_hierarchy = 'issue_date'

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('customer', 'supplier', 'currency')
        qs = qs.annotate(
            balance=F('total') - F('paid_amount')
        )
        return qs

    def entity_name(self, obj):
        return obj.get_related_entity_name()

    entity_name.short_description = _("Mijoz/Ta'minotchi")

    def invoice_type_display(self, obj):
        return obj.get_invoice_type_display()

    invoice_type_display.short_description = _("Turi")

    def status_display(self, obj):
        status_colors = {
            'draft': 'secondary',
            'sent': 'info',
            'paid': 'success',
            'partially_paid': 'primary',
            'cancelled': 'danger',
            'overdue': 'warning',
        }
        color = status_colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.get_status_display())

    status_display.short_description = _("Holati")

    def balance(self, obj):
        return obj.total - obj.paid_amount

    balance.short_description = _("Qolgan summa")

    def view_payments(self, obj):
        url = reverse('admin:finance_payment_changelist') + f'?invoice__id={obj.id}'
        return format_html('<a class="button" href="{}">{}</a>', url, _('To\'lovlarni ko\'rish'))

    view_payments.short_description = _('To\'lovlar')

    def get_fieldsets(self, request, obj=None):
        if obj and obj.invoice_type == 'sales':
            return (
                (None, {
                    'fields': ('number', 'invoice_type', 'status', 'customer', 'order')
                }),
                (_('Sanalar'), {
                    'fields': ('issue_date', 'due_date')
                }),
                (_('Moliyaviy ma\'lumotlar'), {
                    'fields': ('subtotal', 'tax', 'discount', 'total', 'paid_amount', 'currency')
                }),
                (_('Qo\'shimcha'), {
                    'fields': ('notes',)
                }),
            )
        elif obj and obj.invoice_type == 'purchase':
            return (
                (None, {
                    'fields': ('number', 'invoice_type', 'status', 'supplier', 'purchase_order')
                }),
                (_('Sanalar'), {
                    'fields': ('issue_date', 'due_date')
                }),
                (_('Moliyaviy ma\'lumotlar'), {
                    'fields': ('subtotal', 'tax', 'discount', 'total', 'paid_amount', 'currency')
                }),
                (_('Qo\'shimcha'), {
                    'fields': ('notes',)
                }),
            )
        else:
            return (
                (None, {
                    'fields': ('number', 'invoice_type', 'status')
                }),
                (_('Bog\'lanishlar'), {
                    'fields': ('customer', 'supplier', 'order', 'purchase_order')
                }),
                (_('Sanalar'), {
                    'fields': ('issue_date', 'due_date')
                }),
                (_('Moliyaviy ma\'lumotlar'), {
                    'fields': ('subtotal', 'tax', 'discount', 'total', 'paid_amount', 'currency')
                }),
                (_('Qo\'shimcha'), {
                    'fields': ('notes',)
                }),
            )


@admin.register(Payment)
class PaymentAdmin(BaseAdmin):
    list_display = ('number', 'payment_type_display', 'payment_method_display', 'entity_name',
                    'payment_date', 'amount', 'currency_code')
    list_filter = ('payment_type', 'payment_method', 'payment_date')
    search_fields = ('number', 'customer__name', 'supplier__name', 'invoice__number')
    autocomplete_fields = ['customer', 'supplier', 'invoice', 'currency']
    date_hierarchy = 'payment_date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'supplier', 'invoice', 'currency')

    def entity_name(self, obj):
        return obj.get_related_entity_name()

    entity_name.short_description = _("Bog'langan")

    def payment_type_display(self, obj):
        return obj.get_payment_type_display()

    payment_type_display.short_description = _("To'lov turi")

    def payment_method_display(self, obj):
        return obj.get_payment_method_display()

    payment_method_display.short_description = _("To'lov usuli")

    def currency_code(self, obj):
        return obj.currency.code

    currency_code.short_description = _("Valyuta")

    def get_fieldsets(self, request, obj=None):
        if obj and obj.payment_type == 'in':
            return (
                (None, {
                    'fields': ('number', 'payment_type', 'payment_method', 'amount', 'currency')
                }),
                (_('Bog\'lanishlar'), {
                    'fields': ('customer', 'invoice')
                }),
                (_('Ma\'lumot'), {
                    'fields': ('payment_date', 'reference', 'notes')
                }),
            )
        elif obj and obj.payment_type == 'out':
            return (
                (None, {
                    'fields': ('number', 'payment_type', 'payment_method', 'amount', 'currency')
                }),
                (_('Bog\'lanishlar'), {
                    'fields': ('supplier', 'invoice')
                }),
                (_('Ma\'lumot'), {
                    'fields': ('payment_date', 'reference', 'notes')
                }),
            )
        else:
            return (
                (None, {
                    'fields': ('number', 'payment_type', 'payment_method', 'amount', 'currency')
                }),
                (_('Bog\'lanishlar'), {
                    'fields': ('customer', 'supplier', 'invoice')
                }),
                (_('Ma\'lumot'), {
                    'fields': ('payment_date', 'reference', 'notes')
                }),
            )


@admin.register(Expense)
class ExpenseAdmin(BaseAdmin):
    list_display = ('number', 'category_display', 'date', 'amount', 'currency_code', 'description_short')
    list_filter = ('category', 'date')
    search_fields = ('number', 'description', 'reference')
    date_hierarchy = 'date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('currency')

    def category_display(self, obj):
        return obj.get_category_display()

    category_display.short_description = _("Kategoriya")

    def currency_code(self, obj):
        return obj.currency.code

    currency_code.short_description = _("Valyuta")

    def description_short(self, obj):
        if len(obj.description) > 50:
            return obj.description[:50] + '...'
        return obj.description

    description_short.short_description = _("Tavsif")
