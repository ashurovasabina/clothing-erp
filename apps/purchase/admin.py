from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from apps.core.admin import BaseAdmin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem
from django.urls import reverse
from django.utils.html import format_html


@admin.register(Supplier)
class SupplierAdmin(BaseAdmin):
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


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    autocomplete_fields = ['product_variant']
    fields = ('product_variant', 'quantity', 'unit_price', 'received_quantity', 'total_price')
    readonly_fields = ('total_price',)


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(BaseAdmin):
    list_display = ('number', 'supplier', 'order_date', 'status', 'total', 'created_at')
    list_filter = ('status', 'order_date')
    search_fields = ('number', 'supplier__name')
    readonly_fields = ('subtotal', 'total')
    fieldsets = (
        (None, {
            'fields': ('number', 'supplier', 'order_date', 'status', 'warehouse')
        }),
        (_('Yetkazib berish'), {
            'fields': ('expected_date', 'shipping_cost')
        }),
        (_('Moliyaviy ma\'lumotlar'), {
            'fields': ('subtotal', 'discount', 'tax', 'total')
        }),
        (_('Qo\'shimcha'), {
            'fields': ('notes',)
        }),
    )
    inlines = [PurchaseOrderItemInline]
    autocomplete_fields = ['supplier', 'warehouse']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('supplier')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.status not in ['draft', 'sent']:
            # Agar buyurtma tasdiqlangan yoki undan keyingi bosqichda bo'lsa,
            # ba'zi maydonlarni faqat o'qish uchun qilish
            return readonly_fields + ('supplier', 'order_date', 'warehouse')
        return readonly_fields