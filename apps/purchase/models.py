from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel
from apps.inventory.models import ProductVariant, Warehouse
from django_countries.fields import CountryField


class Supplier(BaseModel):
    """Ta'minotchi"""
    name = models.CharField(_("Nomi/Firma"), max_length=200)
    contact_person = models.CharField(_("Kontakt shaxs"), max_length=200, blank=True)
    phone = models.CharField(_("Telefon"), max_length=50)
    email = models.EmailField(_("Email"), blank=True)
    address = models.TextField(_("Manzil"), blank=True)
    city = models.CharField(_("Shahar"), max_length=100, blank=True)
    country = CountryField(_("Davlat"), blank=True)
    tax_number = models.CharField(_("Soliq identifikatori"), max_length=50, blank=True)
    is_active = models.BooleanField(_("Faol"), default=True)
    notes = models.TextField(_("Qo'shimcha ma'lumot"), blank=True)

    class Meta:
        verbose_name = _("Ta'minotchi")
        verbose_name_plural = _("Ta'minotchilar")
        ordering = ['name']

    def __str__(self):
        return self.name


class PurchaseOrder(BaseModel):
    """Xarid buyurtmasi"""
    STATUS_CHOICES = (
        ('draft', _('Qoralama')),
        ('sent', _('Yuborilgan')),
        ('confirmed', _('Tasdiqlangan')),
        ('partially_received', _('Qisman qabul qilingan')),
        ('received', _('Qabul qilingan')),
        ('cancelled', _('Bekor qilingan')),
    )

    number = models.CharField(_("Buyurtma raqami"), max_length=50, unique=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        verbose_name=_("Ta'minotchi")
    )
    order_date = models.DateField(_("Buyurtma sanasi"))
    status = models.CharField(_("Holati"), max_length=20, choices=STATUS_CHOICES, default='draft')
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        verbose_name=_("Ombor")
    )
    expected_date = models.DateField(_("Kutilayotgan sana"), null=True, blank=True)
    notes = models.TextField(_("Izohlar"), blank=True)

    # Moliyaviy ma'lumotlar
    subtotal = models.DecimalField(_("Jami summa"), max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(_("Chegirma"), max_digits=15, decimal_places=2, default=0)
    tax = models.DecimalField(_("Soliq"), max_digits=15, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(_("Yetkazib berish narxi"), max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(_("Yakuniy summa"), max_digits=15, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Xarid buyurtmasi")
        verbose_name_plural = _("Xarid buyurtmalari")
        ordering = ['-order_date', 'number']

    def __str__(self):
        return f"{self.number} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        # Yakuniy summani hisoblash
        self.total = self.subtotal - self.discount + self.tax + self.shipping_cost
        super().save(*args, **kwargs)

    def calculate_subtotal(self):
        """Buyurtma elementlaridan jami summani hisoblash"""
        total = sum(item.total_price for item in self.items.all())
        self.subtotal = total
        self.save()


class PurchaseOrderItem(BaseModel):
    """Xarid buyurtmasi elementi"""
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Xarid buyurtmasi")
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name='purchase_order_items',
        verbose_name=_("Mahsulot varianti")
    )
    quantity = models.PositiveIntegerField(_("Miqdor"), validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(_("Birlik narxi"), max_digits=12, decimal_places=2)
    received_quantity = models.PositiveIntegerField(_("Qabul qilingan miqdor"), default=0)
    total_price = models.DecimalField(_("Umumiy narx"), max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = _("Xarid buyurtmasi elementi")
        verbose_name_plural = _("Xarid buyurtmasi elementlari")

    def __str__(self):
        return f"{self.product_variant} - {self.quantity}"

    def save(self, *args, **kwargs):
        # Umumiy narxni hisoblash
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

        # Buyurtma jami summasini yangilash
        self.purchase_order.calculate_subtotal()