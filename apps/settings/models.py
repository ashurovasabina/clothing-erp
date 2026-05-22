from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel


class CompanyInfo(BaseModel):
    """Kompaniya ma'lumotlari"""
    name = models.CharField(_("Kompaniya nomi"), max_length=200)
    legal_name = models.CharField(_("Yuridik nomi"), max_length=200, blank=True)
    tax_number = models.CharField(_("Soliq identifikatori"), max_length=50, blank=True)
    registration_number = models.CharField(_("Ro'yxatdan o'tish raqami"), max_length=50, blank=True)

    # Aloqa ma'lumotlari
    address = models.TextField(_("Manzil"))
    city = models.CharField(_("Shahar"), max_length=100)
    zip_code = models.CharField(_("Pochta indeksi"), max_length=20, blank=True)
    country = models.CharField(_("Davlat"), max_length=100)

    phone = models.CharField(_("Telefon"), max_length=50)
    email = models.EmailField(_("Email"))
    website = models.URLField(_("Veb-sayt"), blank=True)

    # Logolar
    logo = models.ImageField(_("Logo"), upload_to='company/', blank=True, null=True)
    favicon = models.ImageField(_("Favicon"), upload_to='company/', blank=True, null=True)

    # Bank ma'lumotlari
    bank_name = models.CharField(_("Bank nomi"), max_length=200, blank=True)
    bank_account = models.CharField(_("Bank hisobi"), max_length=50, blank=True)
    bank_code = models.CharField(_("Bank kodi"), max_length=50, blank=True)

    class Meta:
        verbose_name = _("Kompaniya ma'lumotlari")
        verbose_name_plural = _("Kompaniya ma'lumotlari")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Faqat bitta kompaniya ma'lumotlari bo'lishi kerak
        if not self.pk and CompanyInfo.objects.exists():
            # Agar yangi yozuv yaratilyotgan bo'lsa va allaqachon yozuv mavjud bo'lsa
            return
        super().save(*args, **kwargs)


class SystemSetting(BaseModel):
    """Tizim sozlamalari"""
    SETTING_TYPES = (
        ('text', _('Matn')),
        ('number', _('Raqam')),
        ('boolean', _('Mantiqiy')),
        ('date', _('Sana')),
        ('json', _('JSON')),
    )

    key = models.CharField(_("Kalit"), max_length=100, unique=True)
    name = models.CharField(_("Nomi"), max_length=200)
    description = models.TextField(_("Tavsif"), blank=True)
    value_type = models.CharField(_("Qiymat turi"), max_length=20, choices=SETTING_TYPES)

    value_text = models.TextField(_("Matn qiymati"), blank=True)
    value_number = models.DecimalField(_("Raqam qiymati"), max_digits=15, decimal_places=6, null=True, blank=True)
    value_boolean = models.BooleanField(_("Mantiqiy qiymati"), null=True, blank=True)
    value_date = models.DateField(_("Sana qiymati"), null=True, blank=True)
    value_json = models.JSONField(_("JSON qiymati"), null=True, blank=True)

    is_public = models.BooleanField(_("Ommaviy"), default=False,
                                    help_text=_(
                                        "Agar belgilansa, bu sozlama autentifikatsiyasiz foydalanuvchilarga ko'rinadi"))

    class Meta:
        verbose_name = _("Tizim sozlamasi")
        verbose_name_plural = _("Tizim sozlamalari")
        ordering = ['key']

    def __str__(self):
        return f"{self.name} ({self.key})"

    @property
    def value(self):
        """Qiymatni turga qarab qaytarish"""
        if self.value_type == 'text':
            return self.value_text
        elif self.value_type == 'number':
            return self.value_number
        elif self.value_type == 'boolean':
            return self.value_boolean
        elif self.value_type == 'date':
            return self.value_date
        elif self.value_type == 'json':
            return self.value_json
        return None

    def set_value(self, value):
        """Qiymatni turga qarab o'rnatish"""
        if self.value_type == 'text':
            self.value_text = str(value)
        elif self.value_type == 'number':
            self.value_number = value
        elif self.value_type == 'boolean':
            self.value_boolean = bool(value)
        elif self.value_type == 'date':
            self.value_date = value
        elif self.value_type == 'json':
            self.value_json = value