from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from apps.core.admin import BaseAdmin
from .models import (
    Category, Size, Color, Brand, Season,
    Product, ProductVariant, Warehouse, InventoryMovement
)
from django.utils.html import format_html


class SubcategoryInline(admin.TabularInline):
    model = Category
    fk_name = 'parent'
    extra = 1


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ('name', 'parent', 'get_products_count')
    list_filter = ('parent',)
    search_fields = ('name',)
    inlines = [SubcategoryInline]

    def get_products_count(self, obj):
        return obj.products.count()

    get_products_count.short_description = _('Mahsulotlar soni')


@admin.register(Size)
class SizeAdmin(BaseAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Color)
class ColorAdmin(BaseAdmin):
    list_display = ('name', 'color_preview')
    search_fields = ('name',)

    def color_preview(self, obj):
        return format_html(
            '<div style="background-color: {}; width: 30px; height: 15px;"></div>',
            obj.color_code
        )

    color_preview.short_description = _('Rang')


@admin.register(Brand)
class BrandAdmin(BaseAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Season)
class SeasonAdmin(BaseAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('color', 'size', 'sku', 'stock_quantity')


@admin.register(Product)
class ProductAdmin(BaseAdmin):
    list_display = ('code', 'name', 'category', 'brand', 'cost_price', 'wholesale_price', 'is_active')
    list_filter = ('category', 'brand', 'is_active', 'season')
    search_fields = ('code', 'name')
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description', 'category', 'brand', 'season', 'image')
        }),
        (_('Narxlar'), {
            'fields': ('cost_price', 'wholesale_price')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    inlines = [ProductVariantInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'brand')


@admin.register(ProductVariant)
class ProductVariantAdmin(BaseAdmin):
    list_display = ('sku', 'product', 'color', 'size', 'stock_quantity')
    list_filter = ('product__category', 'color', 'size')
    search_fields = ('sku', 'product__name', 'product__code')
    autocomplete_fields = ['product', 'color', 'size']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'color', 'size')


@admin.register(Warehouse)
class WarehouseAdmin(BaseAdmin):
    list_display = ('name', 'address', 'is_main')
    list_filter = ('is_main',)
    search_fields = ('name', 'address')


@admin.register(InventoryMovement)
class InventoryMovementAdmin(BaseAdmin):
    list_display = ('created_at', 'product_variant', 'warehouse', 'movement_type', 'quantity')
    list_filter = ('movement_type', 'warehouse', 'created_at')
    search_fields = ('product_variant__sku', 'product_variant__product__name', 'reference')
    autocomplete_fields = ['product_variant', 'warehouse']
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product_variant', 'warehouse')
