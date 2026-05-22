from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel
from django_countries.fields import CountryField


class Department(BaseModel):
    """Bo'lim"""
    name = models.CharField(_("Nomi"), max_length=100)
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name=_("Bo'lim boshlig'i")
    )
    description = models.TextField(_("Tavsif"), blank=True)

    class Meta:
        verbose_name = _("Bo'lim")
        verbose_name_plural = _("Bo'limlar")
        ordering = ['name']

    def __str__(self):
        return self.name


class Position(BaseModel):
    """Lavozim"""
    name = models.CharField(_("Nomi"), max_length=100)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name=_("Bo'lim")
    )
    description = models.TextField(_("Tavsif"), blank=True)

    class Meta:
        verbose_name = _("Lavozim")
        verbose_name_plural = _("Lavozimlar")
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class Employee(BaseModel):
    """Xodim"""
    GENDER_CHOICES = (
        ('male', _('Erkak')),
        ('female', _('Ayol')),
    )

    first_name = models.CharField(_("Ism"), max_length=100)
    last_name = models.CharField(_("Familiya"), max_length=100)
    middle_name = models.CharField(_("Otasining ismi"), max_length=100, blank=True)
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name='employees',
        verbose_name=_("Lavozim")
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='employees',
        verbose_name=_("Bo'lim")
    )
    hire_date = models.DateField(_("Ishga qabul qilingan sana"))
    birth_date = models.DateField(_("Tug'ilgan sana"), null=True, blank=True)
    gender = models.CharField(_("Jinsi"), max_length=10, choices=GENDER_CHOICES)

    # Aloqa ma'lumotlari
    email = models.EmailField(_("Email"), blank=True)
    phone = models.CharField(_("Telefon"), max_length=50)
    address = models.TextField(_("Manzil"), blank=True)
    city = models.CharField(_("Shahar"), max_length=100, blank=True)
    country = CountryField(_("Davlat"), blank=True)

    # Hujjatlar
    passport_number = models.CharField(_("Pasport raqami"), max_length=50, blank=True)
    tax_id = models.CharField(_("STIR/INN"), max_length=50, blank=True)

    # Rasmlar
    photo = models.ImageField(_("Rasm"), upload_to='employees/', blank=True, null=True)

    # Ish haqi ma'lumotlari
    base_salary = models.DecimalField(
        _("Asosiy ish haqi"),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    # Status
    is_active = models.BooleanField(_("Faol"), default=True)
    notes = models.TextField(_("Qo'shimcha ma'lumot"), blank=True)

    class Meta:
        verbose_name = _("Xodim")
        verbose_name_plural = _("Xodimlar")
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"


class Attendance(BaseModel):
    """Davomatlar"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_("Xodim")
    )
    date = models.DateField(_("Sana"))
    time_in = models.TimeField(_("Kelgan vaqt"), null=True, blank=True)
    time_out = models.TimeField(_("Ketgan vaqt"), null=True, blank=True)
    status = models.CharField(_("Holati"), max_length=20, choices=(
        ('present', _('Kelgan')),
        ('absent', _('Kelmagan')),
        ('half_day', _('Yarim kun')),
        ('late', _('Kechikkan')),
        ('leave', _('Ta\'tilda')),
    ))
    notes = models.TextField(_("Izohlar"), blank=True)

    class Meta:
        verbose_name = _("Davomat")
        verbose_name_plural = _("Davomatlar")
        ordering = ['-date', 'employee']
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.get_status_display()}"


class Salary(BaseModel):
    """Ish haqi to'lovlari"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='salaries',
        verbose_name=_("Xodim")
    )
    month = models.PositiveSmallIntegerField(_("Oy"), choices=[(i, i) for i in range(1, 13)])
    year = models.PositiveIntegerField(_("Yil"))
    base_amount = models.DecimalField(_("Asosiy ish haqi"), max_digits=15, decimal_places=2)
    bonus = models.DecimalField(_("Bonus"), max_digits=15, decimal_places=2, default=0)
    deductions = models.DecimalField(_("Ushlab qolingan"), max_digits=15, decimal_places=2, default=0)
    tax = models.DecimalField(_("Soliqlar"), max_digits=15, decimal_places=2, default=0)
    net_amount = models.DecimalField(_("Qo'lga tegadigan summa"), max_digits=15, decimal_places=2)
    payment_date = models.DateField(_("To'lov sanasi"), null=True, blank=True)
    status = models.CharField(_("Holati"), max_length=20, choices=(
        ('draft', _('Qoralama')),
        ('approved', _('Tasdiqlangan')),
        ('paid', _('To\'langan')),
        ('cancelled', _('Bekor qilingan')),
    ), default='draft')
    notes = models.TextField(_("Izohlar"), blank=True)

    class Meta:
        verbose_name = _("Ish haqi")
        verbose_name_plural = _("Ish haqlari")
        ordering = ['-year', '-month', 'employee']
        unique_together = ['employee', 'month', 'year']

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year} - {self.net_amount}"

    def save(self, *args, **kwargs):
        # Qo'lga tegadigan summani hisoblash
        self.net_amount = self.base_amount + self.bonus - self.deductions - self.tax
        super().save(*args, **kwargs)
