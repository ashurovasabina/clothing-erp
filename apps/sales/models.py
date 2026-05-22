from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel
from apps.inventory.models import ProductVariant, Warehouse
from django_countries.fields import CountryField


class Customer(BaseModel):
    """Mijoz"""
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
        verbose_name = _("Mijoz")
        verbose_name_plural = _("Mijozlar")
        ordering = ['name']

    def __str__(self):
        return self.name


class Order(BaseModel):
    """Buyurtma"""
    STATUS_CHOICES = (
        ('draft', _('Qoralama')),
        ('confirmed', _('Tasdiqlangan')),
        ('processing', _('Jarayonda')),
        ('ready', _('Tayyor')),
        ('shipped', _('Jo\'natilgan')),
        ('delivered', _('Yetkazilgan')),
        ('cancelled', _('Bekor qilingan')),
        ('returned', _('Qaytarilgan')),
    )

    number = models.CharField(_("Buyurtma raqami"), max_length=50, unique=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name=_("Mijoz")
    )
    order_date = models.DateField(_("Buyurtma sanasi"))
    status = models.CharField(_("Holati"), max_length=20, choices=STATUS_CHOICES, default='draft')
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name=_("Ombor")
    )
    shipping_address = models.TextField(_("Yetkazish manzili"), blank=True)
    notes = models.TextField(_("Izohlar"), blank=True)
    estimated_delivery = models.DateField(_("Taxminiy yetkazish sanasi"), null=True, blank=True)

    # Moliyaviy ma'lumotlar
    subtotal = models.DecimalField(_("Jami summa"), max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(_("Chegirma"), max_digits=15, decimal_places=2, default=0)
    tax = models.DecimalField(_("Soliq"), max_digits=15, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(_("Yetkazib berish narxi"), max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(_("Yakuniy summa"), max_digits=15, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Buyurtma")
        verbose_name_plural = _("Buyurtmalar")
        ordering = ['-order_date', 'number']

    def __str__(self):
        return f"{self.number} - {self.customer.name}"

    def save(self, *args, **kwargs):
        # Yakuniy summani hisoblash
        self.total = self.subtotal - self.discount + self.tax + self.shipping_cost
        super().save(*args, **kwargs)

    def calculate_subtotal(self):
        """Buyurtma elementlaridan jami summani hisoblash"""
        total = sum(item.total_price for item in self.items.all())
        self.subtotal = total
        self.save()


class OrderItem(BaseModel):
    """Buyurtma elementi"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Buyurtma")
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_("Mahsulot varianti")
    )
    quantity = models.PositiveIntegerField(_("Miqdor"), validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(_("Birlik narxi"), max_digits=12, decimal_places=2)
    discount_percent = models.DecimalField(_("Chegirma (%)"), max_digits=5, decimal_places=2, default=0)
    total_price = models.DecimalField(_("Umumiy narx"), max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = _("Buyurtma elementi")
        verbose_name_plural = _("Buyurtma elementlari")

    def __str__(self):
        return f"{self.product_variant} - {self.quantity}"

    def save(self, *args, **kwargs):
        # Umumiy narxni hisoblash
        price_after_discount = self.unit_price * (1 - (self.discount_percent / 100))
        self.total_price = price_after_discount * self.quantity
        super().save(*args, **kwargs)

        # Buyurtma jami summasini yangilash
        self.order.calculate_subtotal()
