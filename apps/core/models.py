from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
import uuid


class BaseModel(models.Model):
    """Barcha modellar uchun asosiy abstrakt model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(_("Yaratilgan sana"), auto_now_add=True)
    updated_at = models.DateTimeField(_("O'zgartirilgan sana"), auto_now=True)
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class Currency(BaseModel):
    """Valyuta modeli"""
    code = models.CharField(_("Kod"), max_length=3, unique=True)
    name = models.CharField(_("Nomi"), max_length=100)
    symbol = models.CharField(_("Belgi"), max_length=10, blank=True)
    is_default = models.BooleanField(_("Asosiy"), default=False)

    class Meta:
        verbose_name = _("Valyuta")
        verbose_name_plural = _("Valyutalar")

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Agar yangi valyuta asosiy qilib belgilansa, boshqa barcha valyutalarni asosiy emas qilish
            Currency.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
