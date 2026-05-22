from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel, Currency
from apps.sales.models import Order, Customer
from apps.purchase.models import PurchaseOrder, Supplier
from django.db.models.signals import post_save
from django.dispatch import receiver


class Invoice(BaseModel):
    """Hisob-faktura"""
    TYPE_CHOICES = (
        ('sales', _('Sotuv')),
        ('purchase', _('Xarid')),
    )

    STATUS_CHOICES = (
        ('draft', _('Qoralama')),
        ('sent', _('Yuborilgan')),
        ('paid', _('To\'langan')),
        ('partially_paid', _('Qisman to\'langan')),
        ('cancelled', _('Bekor qilingan')),
        ('overdue', _('Muddati o\'tgan')),
    )

    number = models.CharField(_("Hisob-faktura raqami"), max_length=50, unique=True)
    invoice_type = models.CharField(_("Turi"), max_length=10, choices=TYPE_CHOICES)
    status = models.CharField(_("Holati"), max_length=20, choices=STATUS_CHOICES, default='draft')

    # Bog'lanishlar (faqat bittasi to'ldiriladi)
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='invoices',
        null=True,
        blank=True,
        verbose_name=_("Sotuv buyurtmasi")
    )

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.PROTECT,
        related_name='invoices',
        null=True,
        blank=True,
        verbose_name=_("Xarid buyurtmasi")
    )

    # Mijoz yoki ta'minotchi (faqat bittasi to'ldiriladi)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='invoices',
        null=True,
        blank=True,
        verbose_name=_("Mijoz")
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='invoices',
        null=True,
        blank=True,
        verbose_name=_("Ta'minotchi")
    )

    # Sanalar
    issue_date = models.DateField(_("Chiqarilgan sana"))
    due_date = models.DateField(_("To'lash muddati"))

    # Summa ma'lumotlari
    subtotal = models.DecimalField(_("Jami summa"), max_digits=15, decimal_places=2)
    tax = models.DecimalField(_("Soliq"), max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(_("Chegirma"), max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(_("Yakuniy summa"), max_digits=15, decimal_places=2)

    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name=_("Valyuta")
    )

    # To'langan summa (to'lovlar asosida hisoblanadi)
    paid_amount = models.DecimalField(_("To'langan summa"), max_digits=15, decimal_places=2, default=0)

    notes = models.TextField(_("Izohlar"), blank=True)

    class Meta:
        verbose_name = _("Hisob-faktura")
        verbose_name_plural = _("Hisob-fakturalar")
        ordering = ['-issue_date', 'number']

    def __str__(self):
        return f"{self.number} - {self.get_related_entity_name()}"

    def get_related_entity_name(self):
        """Bog'langan mijoz yoki ta'minotchi nomini qaytaradi"""
        if self.customer:
            return self.customer.name
        elif self.supplier:
            return self.supplier.name
        return ""

    def calculate_balance(self):
        """Qolgan summani hisoblash"""
        return self.total - self.paid_amount

    def update_status_based_on_payments(self):
        """To'lovlar asosida holatni yangilash"""
        balance = self.calculate_balance()

        if balance <= 0:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partially_paid'
        elif self.status != 'draft' and self.status != 'sent' and self.due_date < models.functions.Now():
            self.status = 'overdue'

        self.save(update_fields=['status'])


class Payment(BaseModel):
    """To'lov"""
    PAYMENT_METHODS = (
        ('cash', _('Naqd pul')),
        ('bank_transfer', _('Bank o\'tkazmasi')),
        ('credit_card', _('Kredit karta')),
        ('debit_card', _('Debit karta')),
        ('cheque', _('Chek')),
        ('online', _('Onlayn to\'lov')),
        ('other', _('Boshqa')),
    )

    PAYMENT_TYPES = (
        ('in', _('Kiruvchi')),  # Mijozdan olingan to'lov
        ('out', _('Chiquvchi')),  # Ta'minotchiga to'lov
    )

    number = models.CharField(_("To'lov raqami"), max_length=50, unique=True)
    payment_type = models.CharField(_("To'lov turi"), max_length=10, choices=PAYMENT_TYPES)
    payment_method = models.CharField(_("To'lov usuli"), max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(_("Summa"), max_digits=15, decimal_places=2, validators=[MinValueValidator(0.01)])

    # Bog'lanishlar (faqat bittasi to'ldiriladi)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name='payments',
        null=True,
        blank=True,
        verbose_name=_("Hisob-faktura")
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='payments',
        null=True,
        blank=True,
        verbose_name=_("Mijoz")
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='payments',
        null=True,
        blank=True,
        verbose_name=_("Ta'minotchi")
    )

    payment_date = models.DateField(_("To'lov sanasi"))
    reference = models.CharField(_("Ma'lumotnoma"), max_length=100, blank=True)
    notes = models.TextField(_("Izohlar"), blank=True)

    # Valyuta ma'lumotlari
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name=_("Valyuta")
    )

    class Meta:
        verbose_name = _("To'lov")
        verbose_name_plural = _("To'lovlar")
        ordering = ['-payment_date', 'number']

    def __str__(self):
        return f"{self.number} - {self.get_related_entity_name()} - {self.amount} {self.currency.code}"

    def get_related_entity_name(self):
        """Bog'langan mijoz, ta'minotchi yoki hisob-faktura nomini qaytaradi"""
        if self.invoice:
            return f"Invoice {self.invoice.number}"
        elif self.customer:
            return self.customer.name
        elif self.supplier:
            return self.supplier.name
        return ""


@receiver(post_save, sender=Payment)
def update_invoice_paid_amount(sender, instance, **kwargs):
    """To'lov saqlanganda, hisob-faktura to'langan summasini yangilash"""
    if instance.invoice:
        # Hisob-fakturaga bog'langan barcha to'lovlar summasini hisoblash
        total_paid = instance.invoice.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        # Hisob-fakturani yangilash
        instance.invoice.paid_amount = total_paid
        instance.invoice.save(update_fields=['paid_amount'])

        # To'lovga asoslangan holatni yangilash
        instance.invoice.update_status_based_on_payments()


class Expense(BaseModel):
    """Xarajat"""
    EXPENSE_CATEGORIES = (
        ('rent', _('Ijara')),
        ('utilities', _('Kommunal xizmatlar')),
        ('salaries', _('Ish haqi')),
        ('marketing', _('Marketing')),
        ('transportation', _('Transport')),
        ('maintenance', _('Texnik xizmat')),
        ('insurance', _('Sug\'urta')),
        ('office_supplies', _('Ofis jihozlari')),
        ('taxes', _('Soliqlar')),
        ('other', _('Boshqa')),
    )

    number = models.CharField(_("Xarajat raqami"), max_length=50, unique=True)
    date = models.DateField(_("Xarajat sanasi"))
    category = models.CharField(_("Kategoriya"), max_length=20, choices=EXPENSE_CATEGORIES)
    amount = models.DecimalField(_("Summa"), max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(_("Tavsif"))
    reference = models.CharField(_("Ma'lumotnoma"), max_length=100, blank=True)

    # Valyuta ma'lumotlari
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='expenses',
        verbose_name=_("Valyuta")
    )

    class Meta:
        verbose_name = _("Xarajat")
        verbose_name_plural = _("Xarajatlar")
        ordering = ['-date', 'number']

    def __str__(self):
        return f"{self.number} - {self.get_category_display()} - {self.amount} {self.currency.code}"