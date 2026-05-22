from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from apps.core.admin import BaseAdmin
from .models import Department, Position, Employee, Attendance, Salary
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Sum, Count, Q


class PositionInline(admin.TabularInline):
    model = Position
    extra = 1


@admin.register(Department)
class DepartmentAdmin(BaseAdmin):
    list_display = ('name', 'manager', 'employee_count')
    search_fields = ('name',)
    inlines = [PositionInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('manager')

    def employee_count(self, obj):
        return obj.employees.count()

    employee_count.short_description = _('Xodimlar soni')


@admin.register(Position)
class PositionAdmin(BaseAdmin):
    list_display = ('name', 'department', 'employee_count')
    list_filter = ('department',)
    search_fields = ('name', 'department__name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department')

    def employee_count(self, obj):
        return obj.employees.count()

    employee_count.short_description = _('Xodimlar soni')


@admin.register(Employee)
class EmployeeAdmin(BaseAdmin):
    list_display = ('last_name', 'first_name', 'position', 'department', 'phone', 'is_active')
    list_filter = ('department', 'position', 'is_active', 'gender', 'hire_date')
    search_fields = ('last_name', 'first_name', 'middle_name', 'phone', 'email', 'passport_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': (('first_name', 'last_name', 'middle_name'), 'photo')
        }),
        (_('Ish ma\'lumotlari'), {
            'fields': (('position', 'department'), 'hire_date', 'base_salary', 'is_active')
        }),
        (_('Shaxsiy ma\'lumotlar'), {
            'fields': (('birth_date', 'gender'), ('passport_number', 'tax_id'))
        }),
        (_('Aloqa ma\'lumotlari'), {
            'fields': ('phone', 'email', 'address', 'city', 'country')
        }),
        (_('Qo\'shimcha'), {
            'fields': ('notes',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('position', 'department')

    def view_attendances(self, obj):
        url = reverse('admin:hr_attendance_changelist') + f'?employee__id={obj.id}'
        return format_html('<a class="button" href="{}">{}</a>', url, _('Davomatlarini ko\'rish'))

    view_attendances.short_description = _('Davomatlar')

    def view_salaries(self, obj):
        url = reverse('admin:hr_salary_changelist') + f'?employee__id={obj.id}'
        return format_html('<a class="button" href="{}">{}</a>', url, _('Ish haqlarini ko\'rish'))

    view_salaries.short_description = _('Ish haqlari')


@admin.register(Attendance)
class AttendanceAdmin(BaseAdmin):
    list_display = ('employee', 'date', 'time_in', 'time_out', 'status')
    list_filter = ('status', 'date')
    search_fields = ('employee__last_name', 'employee__first_name', 'notes')
    autocomplete_fields = ['employee']
    date_hierarchy = 'date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee')


@admin.register(Salary)
class SalaryAdmin(BaseAdmin):
    list_display = ('employee', 'month_year', 'base_amount', 'bonus', 'deductions', 'tax', 'net_amount', 'status')
    list_filter = ('status', 'month', 'year')
    search_fields = ('employee__last_name', 'employee__first_name', 'notes')
    autocomplete_fields = ['employee']
    readonly_fields = ('net_amount',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee')

    def month_year(self, obj):
        return f"{obj.month}/{obj.year}"

    month_year.short_description = _('Oy/Yil')