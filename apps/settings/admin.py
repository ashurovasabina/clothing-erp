from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from apps.core.admin import BaseAdmin
from .models import CompanyInfo, SystemSetting
from django.utils.html import format_html


@admin.register(CompanyInfo)
class CompanyInfoAdmin(BaseAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'legal_name', 'tax_number', 'registration_number')
        }),
        (_('Aloqa ma\'lumotlari'), {
            'fields': ('address', 'city', 'zip_code', 'country', 'phone', 'email', 'website')
        }),
        (_('Logolar'), {
            'fields': ('logo', 'favicon')
        }),
        (_('Bank ma\'lumotlari'), {
            'fields': ('bank_name', 'bank_account', 'bank_code')
        }),
    )

    def has_add_permission(self, request):
        # Agar allaqachon kompaniya ma'lumotlari mavjud bo'lsa, yangi yozuv yaratishga ruxsat bermaydi
        return not CompanyInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Kompaniya ma'lumotlarini o'chirishga ruxsat bermaydi
        return False


@admin.register(SystemSetting)
class SystemSettingAdmin(BaseAdmin):
    list_display = ('name', 'key', 'value_type', 'get_value', 'is_public')
    list_filter = ('value_type', 'is_public')
    search_fields = ('name', 'key', 'description')
    readonly_fields = ('key', 'value_type')

    def get_value(self, obj):
        if obj.value_type == 'boolean':
            return format_html('<span style="color: {};">&#9679;</span> {}',
                               'green' if obj.value_boolean else 'red',
                               _('Ha') if obj.value_boolean else _('Yo\'q'))
        elif obj.value_type == 'json':
            return '<JSON>'
        return obj.value

    get_value.short_description = _('Qiymat')

    def get_fieldsets(self, request, obj=None):
        if obj:
            # Mavjud sozlama uchun
            fieldsets = [
                (None, {
                    'fields': ('name', 'key', 'description', 'value_type', 'is_public')
                }),
            ]

            # Qiymat turini tekshirib, tegishli maydonni qo'shish
            if obj.value_type == 'text':
                fieldsets.append(
                    (_('Qiymat'), {'fields': ('value_text',)})
                )
            elif obj.value_type == 'number':
                fieldsets.append(
                    (_('Qiymat'), {'fields': ('value_number',)})
                )
            elif obj.value_type == 'boolean':
                fieldsets.append(
                    (_('Qiymat'), {'fields': ('value_boolean',)})
                )
            elif obj.value_type == 'date':
                fieldsets.append(
                    (_('Qiymat'), {'fields': ('value_date',)})
                )
            elif obj.value_type == 'json':
                fieldsets.append(
                    (_('Qiymat'), {'fields': ('value_json',)})
                )

            return fieldsets
        else:
            # Yangi sozlama uchun
            return [
                (None, {
                    'fields': ('name', 'key', 'description', 'value_type', 'is_public')
                }),
                (_('Qiymatlar'), {
                    'fields': ('value_text', 'value_number', 'value_boolean', 'value_date', 'value_json'),
                    'description': _('Sozlama turiga mos maydonni to\'ldiring.')
                }),
            ]

    def save_model(self, request, obj, form, change):
        # Yangi sozlama uchun kerakli qiymat maydonini aniqlash
        if not change:
            if obj.value_type == 'text' and form.cleaned_data.get('value_text'):
                obj.set_value(form.cleaned_data['value_text'])
            elif obj.value_type == 'number' and form.cleaned_data.get('value_number'):
                obj.set_value(form.cleaned_data['value_number'])
            elif obj.value_type == 'boolean' and form.cleaned_data.get('value_boolean') is not None:
                obj.set_value(form.cleaned_data['value_boolean'])
            elif obj.value_type == 'date' and form.cleaned_data.get('value_date'):
                obj.set_value(form.cleaned_data['value_date'])
            elif obj.value_type == 'json' and form.cleaned_data.get('value_json'):
                obj.set_value(form.cleaned_data['value_json'])

        super().save_model(request, obj, form, change)