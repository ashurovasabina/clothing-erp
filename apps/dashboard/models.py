from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel


class Dashboard(BaseModel):
    """Boshqaruv paneli"""
    name = models.CharField(_("Nomi"), max_length=100)
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='dashboards',
        verbose_name=_("Foydalanuvchi")
    )
    is_default = models.BooleanField(_("Asosiy"), default=False)

    class Meta:
        verbose_name = _("Boshqaruv paneli")
        verbose_name_plural = _("Boshqaruv panellari")
        unique_together = ('name', 'user')

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class DashboardWidget(BaseModel):
    """Dashboard widget"""
    WIDGET_TYPES = (
        ('sales_summary', _('Sotuvlar umumiy')),
        ('top_products', _('Top mahsulotlar')),
        ('inventory_status', _('Inventarizatsiya holati')),
        ('recent_orders', _('So\'nggi buyurtmalar')),
        ('category_distribution', _('Kategoriyalar taqsimoti')),
        ('sales_trend', _('Sotuvlar tendensiyasi')),
        ('customer_stats', _('Mijozlar statistikasi')),
    )

    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets',
        verbose_name=_("Boshqaruv paneli")
    )
    widget_type = models.CharField(_("Widget turi"), max_length=50, choices=WIDGET_TYPES)
    title = models.CharField(_("Sarlavha"), max_length=100)
    position = models.PositiveSmallIntegerField(_("Pozitsiya"))
    col_span = models.PositiveSmallIntegerField(_("Ustun o'lchami"), default=1)
    row_span = models.PositiveSmallIntegerField(_("Qator o'lchami"), default=1)
    settings = models.JSONField(_("Sozlamalar"), default=dict, blank=True)

    class Meta:
        verbose_name = _("Dashboard widget")
        verbose_name_plural = _("Dashboard widgetlar")
        ordering = ['position']

    def __str__(self):
        return f"{self.title} ({self.get_widget_type_display()})"