from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem
from apps.inventory.models import Warehouse, ProductVariant
from apps.core.models import Currency


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'number', 'customer', 'order_date', 'status', 'warehouse',
            'shipping_address', 'estimated_delivery', 'shipping_cost',
            'discount', 'tax', 'notes'
        ]
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'estimated_delivery': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'shipping_address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['warehouse'].queryset = Warehouse.objects.filter(is_active=True)
        self.fields['customer'].queryset = self.fields['customer'].queryset.filter(is_active=True)


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product_variant', 'quantity', 'unit_price', 'discount_percent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_variant'].queryset = ProductVariant.objects.filter(
            stock_quantity__gt=0
        ).select_related('product', 'color', 'size')


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True
)