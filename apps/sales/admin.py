from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from apps.core.admin import BaseAdmin
from .models import Customer, Order, OrderItem
from django.urls import reverse
from django.utils.html import format_html


@admin.register(Customer)
class CustomerAdmin(BaseAdmin):
    list_display = ('name', 'contact_person', 'phone', 'city', 'is_active')
    list_filter = ('is_active', 'country', 'city')
    search_fields = ('name', 'contact_person', 'phone', 'email', 'tax_number')
    fieldsets = (
        (None, {
            'fields': ('name', 'contact_person', 'phone', 'email')
        }),
        (_('Manzil'), {
            'fields': ('address', 'city', 'country')
        }),
        (_('Qo\'shimcha'), {
            'fields': ('tax_number', 'is_active', 'notes')
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ['product_variant']
    fields = ('product_variant', 'quantity', 'unit_price', 'discount_percent', 'total_price')
    readonly_fields = ('total_price',)


@admin.register(Order)
class OrderAdmin(BaseAdmin):
    list_display = ('number', 'customer', 'order_date', 'status', 'total', 'created_at')
    list_filter = ('status', 'order_date')
    search_fields = ('number', 'customer__name')
    readonly_fields = ('subtotal', 'total')
    fieldsets = (
        (None, {
            'fields': ('number', 'customer', 'order_date', 'status', 'warehouse')
        }),
        (_('Yetkazib berish'), {
            'fields': ('shipping_address', 'estimated_delivery', 'shipping_cost')
        }),
        (_('Moliyaviy ma\'lumotlar'), {
            'fields': ('subtotal', 'discount', 'tax', 'total')
        }),
        (_('Qo\'shimcha'), {
            'fields': ('notes',)
        }),
    )
    inlines = [OrderItemInline]
    autocomplete_fields = ['customer', 'warehouse']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer')

    def view_invoices(self, obj):
        """Buyurtmaning hisob-fakturalarini ko'rish uchun tugma"""
        url = reverse('admin:finance_invoice_changelist') + f'?order__id={obj.id}'
        return format_html('<a class="button" href="{}">{}</a>', url, _('Hisob-fakturalarni ko\'rish'))

    view_invoices.short_description = _('Hisob-fakturalar')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.status not in ['draft', 'confirmed']:
            # Agar buyurtma tasdiqlangan yoki undan keyingi bosqichda bo'lsa,
            # ba'zi maydonlarni faqat o'qish uchun qilish
            return readonly_fields + ('customer', 'order_date', 'warehouse')
        return readonly_fields
