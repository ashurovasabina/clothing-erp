from django.db import models
from django.utils.translation import gettext_lazy as _
from colorfield.fields import ColorField
from apps.core.models import BaseModel
from django.core.validators import MinValueValidator


class Category(BaseModel):
    """Kiyim-kechak kategoriyasi"""
    name = models.CharField(_("Nomi"), max_length=100)
    description = models.TextField(_("Tavsif"), blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name=_("Ota kategoriya")
    )
    image = models.ImageField(_("Rasm"), upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name = _("Kategoriya")
        verbose_name_plural = _("Kategoriyalar")
        ordering = ['name']

    def __str__(self):
        return self.name


class Size(BaseModel):
    """Kiyim o'lchami"""
    name = models.CharField(_("Nomi"), max_length=50)
    code = models.CharField(_("Kod"), max_length=10)

    class Meta:
        verbose_name = _("O'lcham")
        verbose_name_plural = _("O'lchamlar")
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Color(BaseModel):
    """Kiyim rangi"""
    name = models.CharField(_("Nomi"), max_length=50)
    color_code = ColorField(_("Rang kodi"), default='#FFFFFF')

    class Meta:
        verbose_name = _("Rang")
        verbose_name_plural = _("Ranglar")
        ordering = ['name']

    def __str__(self):
        return self.name


class Brand(BaseModel):
    """Kiyim brendi"""
    name = models.CharField(_("Nomi"), max_length=100)
    description = models.TextField(_("Tavsif"), blank=True)
    logo = models.ImageField(_("Logo"), upload_to='brands/', blank=True, null=True)

    class Meta:
        verbose_name = _("Brend")
        verbose_name_plural = _("Brendlar")
        ordering = ['name']

    def __str__(self):
        return self.name


class Season(BaseModel):
    """Mavsum"""
    name = models.CharField(_("Nomi"), max_length=50)

    class Meta:
        verbose_name = _("Mavsum")
        verbose_name_plural = _("Mavsumlar")

    def __str__(self):
        return self.name


class Product(BaseModel):
    """Kiyim mahsuloti"""
    code = models.CharField(_("Artikul"), max_length=50, unique=True)
    name = models.CharField(_("Nomi"), max_length=200)
    description = models.TextField(_("Tavsif"), blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_("Kategoriya")
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_("Brend")
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_("Mavsum")
    )
    cost_price = models.DecimalField(
        _("Tannarx"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    wholesale_price = models.DecimalField(
        _("Ulgurji narx"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(_("Faol"), default=True)
    image = models.ImageField(_("Asosiy rasm"), upload_to='products/', blank=True, null=True)

    class Meta:
        verbose_name = _("Mahsulot")
        verbose_name_plural = _("Mahsulotlar")
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def profit_margin(self):
        """Foyda marjasi foizda"""
        if self.cost_price > 0:
            return ((self.wholesale_price - self.cost_price) / self.cost_price) * 100
        return 0


class ProductVariant(BaseModel):
    """Mahsulot varianti (rang, o'lcham)"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_("Mahsulot")
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        related_name='product_variants',
        verbose_name=_("Rang")
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.PROTECT,
        related_name='product_variants',
        verbose_name=_("O'lcham")
    )
    sku = models.CharField(_("SKU"), max_length=100, unique=True)
    stock_quantity = models.PositiveIntegerField(_("Ombordagi miqdor"), default=0)
    image = models.ImageField(_("Variant rasmi"), upload_to='product_variants/', blank=True, null=True)

    class Meta:
        verbose_name = _("Mahsulot varianti")
        verbose_name_plural = _("Mahsulot variantlari")
        unique_together = ('product', 'color', 'size')

    def __str__(self):
        return f"{self.product.code} - {self.color.name} - {self.size.name}"


class Warehouse(BaseModel):
    """Ombor"""
    name = models.CharField(_("Nomi"), max_length=100)
    address = models.TextField(_("Manzil"), blank=True)
    is_main = models.BooleanField(_("Asosiy ombor"), default=False)

    class Meta:
        verbose_name = _("Ombor")
        verbose_name_plural = _("Omborlar")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_main:
            # Agar yangi ombor asosiy qilib belgilansa, boshqa barcha omborlarni asosiy emas qilish
            Warehouse.objects.filter(is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class InventoryMovement(BaseModel):
    """Ombor harakati"""
    MOVEMENT_TYPES = (
        ('in', _('Kirim')),
        ('out', _('Chiqim')),
        ('transfer', _('Ko\'chirish')),
        ('adjustment', _('Moslash')),
    )

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name='movements',
        verbose_name=_("Mahsulot varianti")
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='movements',
        verbose_name=_("Ombor")
    )
    movement_type = models.CharField(_("Harakat turi"), max_length=10, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField(_("Miqdor"))
    reference = models.CharField(_("Havola"), max_length=100, blank=True)
    notes = models.TextField(_("Izohlar"), blank=True)

    class Meta:
        verbose_name = _("Ombor harakati")
        verbose_name_plural = _("Ombor harakatlari")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product_variant} - {self.quantity}"
